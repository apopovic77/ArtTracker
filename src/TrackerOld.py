
import config
import cv2
from ultralytics import YOLO
import supervision as sv
from supervision.geometry.core import Point
import logging
import threading
import numpy as np
from CaptureWebCamImage import WarpTransform
src = np.array([[ 604.,  205.],
                [1089.,  214.],
                [1514.,  909.],
                [  12.,  909.]], dtype=np.float32)
dst = np.array([[ 163.,   89.],
                [1465.,   88.],
                [1468.,  826.],
                [ 160.,  825.]], dtype=np.float32)
warptransform = WarpTransform(src,dst)
WithWarpTransform = True

from protobuf.TrackedPerson_pb2 import TrackedPerson
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime

from Midi.MidiController import MidiController
midi = MidiController.getInstance()
midi.start_keyboard_listener()

from Zmq.PubService import PubService
pubservice = PubService()

from Utility.FPSCounter import FPSCounter
fps_counter = FPSCounter()

from Utility.WebcamInfo import WebcamInfo
webcam = WebcamInfo()

import torch

# import asyncio
dispatcher_lock = threading.Lock()
from time import sleep
# from concurrent.futures import ProcessPoolExecutor

# Create a new queue
import queue
tracked_persons = queue.Queue()

from Utility.Logger import Logger
logger = Logger()

from Tcp.Server import TcpServer
server = TcpServer()

from SharedMemoryManager import SharedMemoryManager
shm_manager = SharedMemoryManager(max_players=10)

from Rabbit.RabbitMessageBroker import RabbitMessageBroker

from PersonLocation import PersonLocation, Area, Event
AREA_WIDTH = 1/config.AREAS_COUNT
Area.SetArea(config.AREAS_COUNT)
person_locations = {}


from Hmm.HMM import RealTimeHMM
hmm = RealTimeHMM()
debug_states = np.zeros((200, config.IMAGE_WIDTH, 3), dtype=np.uint8)
from Hmm.HMMRadial import RadialHMM
hmmr = RadialHMM(n_areas=6, start_angle=np.pi/10)
hmmr.print_transition_matrix()
hmmr.draw_areas(500, np.pi/10, -np.pi/10)





# Set the desired logging level
logging.getLogger("ultralytics").setLevel(logging.WARNING)
logging.getLogger("torch").setLevel(logging.WARNING)
logging.getLogger("torchvision").setLevel(logging.WARNING)
    
def draw_prediction_rectangle(frame, state, rectangle_height=100, color=(0, 255, 0), thickness=2):
    # Determine the width and height of the rectangle based on the image size and area proportions
    image_width = frame.shape[1]
    rectangle_width = int(image_width * AREA_WIDTH)

    if(state is None):
        return

    # Determine the x-coordinate for the top-left corner of the rectangle based on the state
    x = int((state - 1) * image_width * AREA_WIDTH) if state > 0 else 0

    # Determine the y-coordinate for the top-left corner of the rectangle
    y = 100  # Update with your desired y-coordinate

    # Draw the rectangle on the image
    cv2.rectangle(frame, (x, y), (x + rectangle_width, y + rectangle_height), color, thickness=thickness)

    return frame

def draw_text(frame, text, state, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1.0, color=(0, 255, 0), thickness=2):
    image_width = frame.shape[1]
    x = int((state - 1) * image_width * AREA_WIDTH) if state > 0 else 0
    y = 100  # Update with your desired y-coordinate
    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
    text_x = x - text_size[0] // 2
    text_y = y + text_size[1] // 2
    cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, thickness)



def create_person(xyxy,tracker_id):
    x1 = xyxy[0]
    y1 = xyxy[1]
    x2 = xyxy[2]
    y2 = xyxy[3]

    current_time = datetime.now()
    timestamp = Timestamp()
    timestamp.FromDatetime(current_time)

    tracked_person = TrackedPerson()
    tracked_person.boundingbox.x = x1/webcam.width
    tracked_person.boundingbox.y = y1/webcam.height
    tracked_person.boundingbox.width = (x2-x1)/webcam.width
    tracked_person.boundingbox.height = (y2-y1)/webcam.height
    tracked_person.id = tracker_id
    tracked_person.timestamp.CopyFrom(timestamp)
    return tracked_person


def send_message(person):
    dispatcher_lock.acquire()
    tracked_persons.put(person)
    dispatcher_lock.release()


def do_send_with_zmq(tracked_person):
    #print("PERSON "+str(tracked_person.id) + f" x: {tracked_person.boundingbox.x:.2f}, y: {tracked_person.boundingbox.y:.2f}, width: {tracked_person.boundingbox.width:.2f}, height: {tracked_person.boundingbox.height:.2f} ", end='')
    pubservice.send("TrackedPerson",tracked_person)
    #RabbitMessageBroker.send_to_shared_mem(tracked_person)

def start_dispatcher():
    while(True):
        dispatcher_lock.acquire()
        if tracked_persons.qsize() > 0:
            tp = tracked_persons.get()
            do_send_with_zmq(tp)
        dispatcher_lock.release()
        sleep(60.0/1000)

def on_location_changed(sender, new_location):
    person_location = sender
    if(person_location not in person_locations):
        person_location.LocationChanged -= on_location_changed



    # Event handler code
    print(f"Location changed: person id {person_location.observations[-1].id} {new_location}")

def main():

    #server.Run()

    if(webcam.IsWebcamAvailable == False):
        print("cannot run no camera connected")
        return

    # # Start the dispatcher in a parallel thread
    # dispatcher_thread = threading.Thread(target=start_dispatcher)
    # dispatcher_thread.start()
   
    # #start the publisher server
    # pubservice.run_server()


    # Usage
    print(f"Webcam resolution: {webcam.width}x{webcam.height}")


    #this is needed for the labeling the images
    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=1,
        text_scale=0.5
    )

    #the yolo model
    model = YOLO("yolov8l.pt")
    
    device = "mps"
    if torch.cuda.is_available():
        device = 0


    imgsz = 320  # Reduce input image size for faster processing
    classes = [0]  # Filter detections to class 0 (persons)
    conf = 0.3  # Adjust confidence threshold for detection stability
    iou = 0.5  # Adjust IoU threshold for NMS

        #work on each frame separatly
    for result in model.track(
        source=str(config.WEBCAM_IDX), 
        show=config.SHOWCV, 
        stream=True, 
        device=device
        , 
        imgsz=imgsz, 
        classes=classes,
        conf=conf,
        iou=iou
        ):
        try:
            frame = result.orig_img
            
            #annotate the image        
            detections = sv.Detections.from_ultralytics(result)
            if result.boxes.id is not None:
                detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)
            labels = []
            detections_for_labels = []

            current_tracks = []  
            count_detections = len(detections)
            for i in range(count_detections):
                confidence = detections[i].confidence[0]
                class_id = detections[i].class_id[0]
                label = "#"+str(detections[i].tracker_id)+model.model.names[class_id] + " " + f"{confidence:.2f}"
                
                if class_id == 0 and confidence > config.CONFIDENCE_DETECTION_MIN and detections[i].tracker_id is not None: 
                    #send message via publish service zmq
                    person = create_person(detections[i].xyxy[0],detections[i].tracker_id[0])

                    person_centerx = person.boundingbox.x + person.boundingbox.width/2
                    person_centery = person.boundingbox.y + person.boundingbox.height/2

                    person_loc = None
                    labels.append(label)
                    detections_for_labels.append(detections[i])
                    if person.id not in person_locations:
                        person_loc = PersonLocation(person.id)
                        person_locations[person.id] = person_loc
                        # Subscribe to the LocationChanged event
                        person_loc.LocationChanged += on_location_changed
                    else:
                        person_loc = person_locations[person.id]

                    location_changed = person_loc.update(person)
                    if(location_changed == True):
                        print("PERSON "+str(person.id)+" in Area "+Area.StateNames[person_loc.last_location])
                    current_tracks.append(person)
                    send_message(person)


                    #transform according to warp transform
                    if (warptransform.has_warp() and WithWarpTransform):
                        print ("PERSON "+str(person.id)+" "+str(person_loc.UniquePersonId) + " CENTER " + str(person_centerx*config.IMAGE_WIDTH) + " " + str(person_centery*config.IMAGE_HEIGHT))
                        (person_centerx,person_centery) = warptransform.transform_point((person_centerx*config.IMAGE_WIDTH, person_centery*config.IMAGE_HEIGHT))
                        print ("PERSON "+str(person.id)+" "+str(person_loc.UniquePersonId)+ " CENTER " + str(person_centerx)+ " "+ str(person_centery))
                        print ("**********")
                    shm_manager.update_player(person.id, person_loc.UniquePersonId, person_centerx / config.IMAGE_WIDTH, person_centery / config.IMAGE_HEIGHT)
                    




                    #hmm.update((person.boundingbox.x + person.boundingbox.width/2))
                    #hmmr.update(person.boundingbox.x + person.boundingbox.width/2, person.boundingbox.y + person.boundingbox.height/2)
                    #print(person.boundingbox.x + person.boundingbox.width/2) 

                    
                    #if len(hmm.observations) == 500:
                        # hmm.train()
                        # hmm.print_transition_matrix()
            
            if len(current_tracks) > 0:
                server.add_persons(current_tracks)

            shm_manager.write_to_shared_memory()
                
            # Update the FPS counter
            fps_counter.update()
            # Print the current FPS
            #fps_counter.print_fps()

            # check for people that left
            debug_states = np.zeros((200, config.IMAGE_WIDTH, 3), dtype=np.uint8)
            person_locations_copy = list(person_locations.values())
            for index, person_location in enumerate(person_locations_copy):
                person = person_location.observations[-1]
                person_id = person.id
                if(person_location.HasLeft()==True):
                    del person_locations[person_id]
                    print("PERSON "+str(person.id) + "HAS LEFT")
                else:
                    bb = person.boundingbox
                    point = Point(x=int((bb.x + bb.width/2)*config.IMAGE_WIDTH),y=int((bb.y+bb.height/2)*config.IMAGE_HEIGHT))
                    in_area = person_location.IsInArea()
                    text = Area.StateNames[in_area]
                    sv.draw_text(scene=frame, text_anchor=point, text=text)
                    draw_prediction_rectangle(frame=debug_states, state=in_area,color=person_location.color, rectangle_height=50)   
                    draw_text(frame=debug_states, state=in_area, text="PersonId "+str(person_id),color=person_location.color)
                    
                
            draw_text(frame=debug_states, state=1, text=fps_counter.get_fps_string())
            cv2.imshow("Empty Image", debug_states)          
            #frame = box_annotator.annotate(scene=frame, detections=detections_for_labels, labels=labels)




            



            #cv2.imshow("yolov8",frame)



            #with esc you can escape and quit the app
            if(cv2.waitKey(30) == 27):
                break

        except Exception as e:
            print("===========================")
            print( "error exception:", str(e) )
            print("===========================")





if __name__ == "__main__":
    main()