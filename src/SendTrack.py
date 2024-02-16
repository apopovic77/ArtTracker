import config
import numpy as np
from pandas import Timestamp
import cv2
from typing import Optional, Tuple
import numpy as np

from Utility.WebcamInfo import WebcamInfo
from supervision.geometry.core import Point

from protobuf.TrackedPerson_pb2 import TrackedPerson
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime

from SharedMemoryManager import SharedMemoryManager
from OscClient import OscComm

from NumberPool import NumberPool
numberpool = NumberPool(config.NUMBERPOOLSIZE)



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







from PersonLocation import PersonLocation, Area, Event
AREA_WIDTH = 1/config.AREAS_COUNT
Area.SetArea(config.AREAS_COUNT)








class SendTrack:
    def __init__(self,webcam):
        self.pipe_name = ""
        self.webcam = webcam
        self.person_locations = {}
        self.shm_manager = SharedMemoryManager(max_players=10)
        
        self.osc = OscComm(config.OSC_ADDRESS, config.OSC_PORT, fps=config.OSC_FPS)  # Adjust IP, port, and desired FPS
        if(config.OSC_RUN):
            self.osc.start_client()

        

    def send(self,boxes, track_ids, masks, triangles, pose_center_points, image):
        dbg_text = ""

        for box, track_id, mask, tria, pose_center in zip(boxes, track_ids, masks, triangles, pose_center_points):
            x, y, w, h = box


            #send message via publish service zmq
            person = self.create_person(box,track_id, pose_center)




            person_centerx = (person.boundingbox.x + person.boundingbox.width/2) * config.IMAGE_WIDTH
            person_centery = (person.boundingbox.y + person.boundingbox.height/2) * config.IMAGE_HEIGHT

            # if pose_center is not None:
            #     person_centerx = pose_center[0] * config.IMAGE_WIDTH
            #     person_centery = pose_center[1] * config.IMAGE_HEIGHT
            
                
            self.draw_prediction_circle(frame=image, pos=Point(person_centerx, person_centery))
  

            person_location = None
            if person.id not in self.person_locations:
                person_location = PersonLocation(person.id)
                self.person_locations[person.id] = person_location
                # Subscribe to the LocationChanged event
                person_location.LocationChanged += self.on_location_changed
            else:
                person_location = self.person_locations[person.id]

            location_changed = person_location.update(person)
            if(location_changed == True):
                print("PERSON "+str(person.id)+" in Area "+Area.StateNames[person_location.last_location])

            if config.WITH_SHARED_MEM:
                self.shm_manager.update_player(person.id, person_location.UniquePersonId, person_centerx / config.IMAGE_WIDTH, person_centery / config.IMAGE_HEIGHT, mask, tria)


            dbg_text += "PERSON TrackId:"+str(person.id)+" UniqueID:"+str(person_location.UniquePersonId) + " PoolId:"+str(person_location.PoolId)+" CENTER " + str(person_centerx) + " " + str(person_centery)+"\n\r"
            

            if(person_location.PoolId >= 0):
                self.osc.add_message("/composition/layers/"+str(person_location.PoolId)+"/video/opacity", person_centerx / config.IMAGE_WIDTH)
            #self.osc.add_message("/composition/layers/2/video/opacity", person_centery / config.IMAGE_HEIGHT)
        #/composition/layers/3/video/opacity
        self.debugprint_into_image(image,dbg_text) 
        #now flush it to the pipe
        self.shm_manager.write_to_shared_memory()  

        

        # check for people that left
        debug_states = np.zeros((200, config.IMAGE_WIDTH, 3), dtype=np.uint8)
        person_locations_copy = list(self.person_locations.values())
        for index, person_location in enumerate(person_locations_copy):
            person = person_location.observations[-1]
            person_id = person.id
            if(person_location.HasLeft()==True):
                NumberPool.getInstance().close(person_location.PoolId)
                del self.person_locations[person_id]
                
                for key,pl in self.person_locations.items():
                    if(pl.PoolId < 0):
                        pl.PoolId = NumberPool.getInstance().getNextFree()
                        break
                
                print("PERSON "+str(person.id) + "HAS LEFT")
            else:
                bb = person.boundingbox

                #point = Point(x=int((bb.x + bb.width/2)*config.IMAGE_WIDTH),y=int((bb.y+bb.height/2)*config.IMAGE_HEIGHT))
                point = Point(person_centerx,person_centery)
                
                in_area = person_location.IsInArea()
                text = Area.StateNames[in_area]
                #sv.draw_text(scene=image, text_anchor=point, text=text)
                self.draw_prediction_rectangle(frame=image, state=in_area,color=person_location.color, rectangle_height=50)   
                self.draw_text(frame=image, state=in_area, text="TrackId:"+str(person.id)+"\nUniqueID:"+str(person_location.UniquePersonId) + "\nPoolId:"+str(person_location.PoolId),color=person_location.color)




    def debugprint_into_image(self,image, text):
        # Configuration for the text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        color = (255, 0, 0)  # Blue, Green, Red
        self.add_text_to_image(image, text,(0,0), font_scale,font_color_rgb=color,line_spacing=0.5)

        

    def draw_text(self,frame, text, state, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1.0, color=(0, 255, 0), thickness=2):
        image_width = frame.shape[1]
        x = int((state - 1) * image_width * AREA_WIDTH) if state > 0 else 0
        y = 100  # Update with your desired y-coordinate
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_x = x - text_size[0] // 2
        text_y = y + text_size[1] // 2
        self.add_text_to_image(frame, text,(text_x, text_y), font_scale,font_color_rgb=color,line_spacing=0.7, font_face=font,font_thickness=thickness)
        #cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, thickness)

    def draw_prediction_rectangle(self,frame, state, rectangle_height=100, color=(0, 255, 0), thickness=2):
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
    
    def draw_prediction_circle(self,frame, pos, color=(0, 255, 0)):
        # Determine the width and height of the rectangle based on the image size and area proportions
        image_width = frame.shape[1]
        x = int(pos.x)
        y = int(pos.y)
        # Draw the rectangle on the image
        cv2.circle(frame, center=(x,y), radius=20, color=color,thickness=4)

        return frame        



    def on_location_changed(self, sender, new_location):
        person_location = sender
        if(person_location not in self.person_locations):
            person_location.LocationChanged -= self.on_location_changed
        # Event handler code
        print(f"Location changed: person id {person_location.observations[-1].id} {new_location}")

    
    def create_person(self,box,tracker_id, pose_center):
        x, y, w, h = box

        current_time = datetime.now()
        timestamp = Timestamp()
        timestamp.FromDatetime(current_time)

        person_centerx = x
        person_centery = y

        if(pose_center is not None and len(pose_center) > 1):
            person_centerx = pose_center[0]*self.webcam.width
            person_centery = pose_center[1]*self.webcam.height

        #transform according to warp transform
        if (warptransform.has_warp() and config.WITH_WARP_TRANSFORM):
            (person_centerx,person_centery) = warptransform.transform_point((person_centerx, person_centery))

        tracked_person = TrackedPerson()
        tracked_person.boundingbox.x = (person_centerx-w/2)/self.webcam.width
        tracked_person.boundingbox.y = (person_centery-h/2)/self.webcam.height

        tracked_person.boundingbox.width = w/self.webcam.width
        tracked_person.boundingbox.height = h/self.webcam.height
        tracked_person.id = tracker_id
        tracked_person.timestamp.CopyFrom(timestamp)
        return tracked_person
    



    def add_text_to_image(self,
        image_rgb: np.ndarray,
        label: str,
        top_left_xy: Tuple = (0, 0),
        font_scale: float = 1,
        font_thickness: float = 1,
        font_face=cv2.FONT_HERSHEY_SIMPLEX,
        font_color_rgb: Tuple = (0, 0, 255),
        bg_color_rgb: Optional[Tuple] = None,
        outline_color_rgb: Optional[Tuple] = None,
        line_spacing: float = 1,
    ):
        """
        Adds text (including multi line text) to images.
        You can also control background color, outline color, and line spacing.

        outline color and line spacing adopted from: https://gist.github.com/EricCousineau-TRI/596f04c83da9b82d0389d3ea1d782592
        """
        OUTLINE_FONT_THICKNESS = 3 * font_thickness

        im_h, im_w = image_rgb.shape[:2]

        for line in label.splitlines():
            x, y = top_left_xy

            # ====== get text size
            if outline_color_rgb is None:
                get_text_size_font_thickness = font_thickness
            else:
                get_text_size_font_thickness = OUTLINE_FONT_THICKNESS

            (line_width, line_height_no_baseline), baseline = cv2.getTextSize(
                line,
                font_face,
                font_scale,
                get_text_size_font_thickness,
            )
            line_height = line_height_no_baseline + baseline

            if bg_color_rgb is not None and line:
                # === get actual mask sizes with regard to image crop
                if im_h - (y + line_height) <= 0:
                    sz_h = max(im_h - y, 0)
                else:
                    sz_h = line_height

                if im_w - (x + line_width) <= 0:
                    sz_w = max(im_w - x, 0)
                else:
                    sz_w = line_width

                # ==== add mask to image
                if sz_h > 0 and sz_w > 0:
                    bg_mask = np.zeros((sz_h, sz_w, 3), np.uint8)
                    bg_mask[:, :] = np.array(bg_color_rgb)
                    image_rgb[
                        y : y + sz_h,
                        x : x + sz_w,
                    ] = bg_mask

            # === add outline text to image
            if outline_color_rgb is not None:
                image_rgb = cv2.putText(
                    image_rgb,
                    line,
                    (x, y + line_height_no_baseline),  # putText start bottom-left
                    font_face,
                    font_scale,
                    outline_color_rgb,
                    OUTLINE_FONT_THICKNESS,
                    cv2.LINE_AA,
                )
            # === add text to image
            image_rgb = cv2.putText(
                image_rgb,
                line,
                (x, y + line_height_no_baseline),  # putText start bottom-left
                font_face,
                font_scale,
                font_color_rgb,
                font_thickness,
                cv2.LINE_AA,
            )
            top_left_xy = (x, y + int(line_height * line_spacing))

        return image_rgb


