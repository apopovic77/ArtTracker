import config
import numpy as np
from pandas import Timestamp

from Utility.WebcamInfo import WebcamInfo
from supervision.geometry.core import Point

from protobuf.TrackedPerson_pb2 import TrackedPerson
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime

from SharedMemoryManager import SharedMemoryManager



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






from PersonLocation import PersonLocation, Area, Event
AREA_WIDTH = 1/config.AREAS_COUNT
Area.SetArea(config.AREAS_COUNT)








class SendTrack:
    def __init__(self,webcam):
        self.pipe_name = ""
        self.webcam = webcam
        self.person_locations = {}
        self.shm_manager = SharedMemoryManager(max_players=10)


    def send(self,boxes,track_ids):
        for box, track_id in zip(boxes, track_ids):
            x, y, w, h = box

            #send message via publish service zmq
            person = self.create_person(box,track_id)

            person_centerx = person.boundingbox.x + person.boundingbox.width/2
            person_centery = person.boundingbox.y + person.boundingbox.height/2

            person_loc = None
            if person.id not in self.person_locations:
                person_loc = PersonLocation(person.id)
                self.person_locations[person.id] = person_loc
                # Subscribe to the LocationChanged event
                person_loc.LocationChanged += self.on_location_changed
            else:
                person_loc = self.person_locations[person.id]

            location_changed = person_loc.update(person)
            if(location_changed == True):
                print("PERSON "+str(person.id)+" in Area "+Area.StateNames[person_loc.last_location])

            #transform according to warp transform
            if (warptransform.has_warp() and WithWarpTransform):
                print ("PERSON "+str(person.id)+" "+str(person_loc.UniquePersonId) + " CENTER " + str(person_centerx*config.IMAGE_WIDTH) + " " + str(person_centery*config.IMAGE_HEIGHT))
                (person_centerx,person_centery) = warptransform.transform_point((person_centerx*config.IMAGE_WIDTH, person_centery*config.IMAGE_HEIGHT))
                print ("PERSON "+str(person.id)+" "+str(person_loc.UniquePersonId)+ " CENTER " + str(person_centerx)+ " "+ str(person_centery))
                print ("**********")
            self.shm_manager.update_player(person.id, person_loc.UniquePersonId, person_centerx / config.IMAGE_WIDTH, person_centery / config.IMAGE_HEIGHT)
        
        
        #now flush it to the pipe
        self.shm_manager.write_to_shared_memory()  


        # check for people that left
        debug_states = np.zeros((200, config.IMAGE_WIDTH, 3), dtype=np.uint8)
        person_locations_copy = list(self.person_locations.values())
        for index, person_location in enumerate(person_locations_copy):
            person = person_location.observations[-1]
            person_id = person.id
            if(person_location.HasLeft()==True):
                del self.person_locations[person_id]
                print("PERSON "+str(person.id) + "HAS LEFT")
            else:
                bb = person.boundingbox
                point = Point(x=int((bb.x + bb.width/2)*config.IMAGE_WIDTH),y=int((bb.y+bb.height/2)*config.IMAGE_HEIGHT))
                in_area = person_location.IsInArea()
                text = Area.StateNames[in_area]
  
    
    def on_location_changed(self, sender, new_location):
        person_location = sender
        if(person_location not in self.person_locations):
            person_location.LocationChanged -= self.on_location_changed
        # Event handler code
        print(f"Location changed: person id {person_location.observations[-1].id} {new_location}")

    
    def create_person(self,box,tracker_id):
        x, y, w, h = box

        current_time = datetime.now()
        timestamp = Timestamp()
        timestamp.FromDatetime(current_time)

        tracked_person = TrackedPerson()
        tracked_person.boundingbox.x = x/self.webcam.width
        tracked_person.boundingbox.y = y/self.webcam.height
        tracked_person.boundingbox.width = w/self.webcam.width
        tracked_person.boundingbox.height = h/self.webcam.height
        tracked_person.id = tracker_id
        tracked_person.timestamp.CopyFrom(timestamp)
        return tracked_person

