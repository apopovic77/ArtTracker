import cv2
from ultralytics import YOLO
import supervision as sv
import logging

from TrackedPerson_pb2 import TrackedPerson
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime

from PubService import PubService
pubservice = PubService()


from WebcamInfo import WebcamInfo
webcam = WebcamInfo()

# Set the desired logging level
logging.getLogger("ultralytics").setLevel(logging.WARNING)
logging.getLogger("torch").setLevel(logging.WARNING)
logging.getLogger("torchvision").setLevel(logging.WARNING)


def send_message(xyxy,tracker_id):
        try:
            x1 = xyxy[0]
            y1 = xyxy[1]
            x2 = xyxy[2]
            y2 = xyxy[3]

            #print("PERSON "+str(tracker_id) + f" x1: {x1:.2f}, y1: {y1:.2f}, x2: {x2:.2f}, y2: {y2:.2f}")
 
            # Get the current time
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
            
            print("PERSON "+str(tracker_id) + f" x: {tracked_person.boundingbox.x:.2f}, y: {tracked_person.boundingbox.y:.2f}, width: {tracked_person.boundingbox.width:.2f}, height: {tracked_person.boundingbox.height:.2f}")

            pubservice.send("TrackedPerson",tracked_person)
        except Exception as e:
            # Exception handling code for other exceptions
            print("===========================")
            print("An error occurred:", str(e))
            print("===========================")

def main():

    if(webcam.IsWebcamAvailable == False):
        print("cannot run no camera connected")
        return



    # Usage
    print(f"Webcam resolution: {webcam.width}x{webcam.height}")


    #start the publisher server
    pubservice.run_server()

    #this is needed for the labeling the images
    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=1,
        text_scale=0.5
    )

    #the yolo model
    model = YOLO("yolov8l.pt")
    
    #work on each frame separatly
    for result in model.track(source="0", show=False, stream=True):
        try:
            frame = result.orig_img
            
            #annotate the image        
            detections = sv.Detections.from_yolov8(result)
            if result.boxes.id is not None:
                detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)
            labels = []
            for i in range(len(detections)):
                confidence = detections[i].confidence[0]
                class_id = detections[i].class_id[0]
                label = "#"+str(detections[i].tracker_id)+model.model.names[class_id] + " " + f"{confidence:.2f}"
                labels.append(label)
                
                if class_id == 0 and confidence > 0.7 and detections[i].tracker_id is not None: 
                    #send message via publish service zmq
                    send_message(detections[i].xyxy[0],detections[i].tracker_id[0])
                
            frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)
            
            cv2.imshow("yolov8",frame)

            #with esc you can escape and quit the app
            if(cv2.waitKey(30) == 27):
                break

        except Exception as e:
            print("===========================")
            print( "error exception:", str(e) )
            print("===========================")




    # model = YOLO('yolov8n.pt')  # load an official detection model
    # results = model.track(source="https://youtu.be/Zgi9g1ksQHc", show=True)     

if __name__ == "__main__":
    main()