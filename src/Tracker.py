from collections import defaultdict
from protobuf.TrackedPerson_pb2 import TrackedPerson
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime
import numpy as np
from Triangulation import Triangulation
import sys
import os
import config
from Utility.FPSCounter import FPSCounter
import logging
from FpsController import FpsController
from Midi.MidiController import MidiController
from configgui import ConfigGUI
from Utility.WebcamInfo import WebcamInfo
import cv2
import numpy as np
import time
from ultralytics import YOLO
from SendTrack import SendTrack
import queue
from OpenCVWindowUtility import Utility
import torch
import gc
import tripy
from pydantic import BaseModel
import numpy as np  # Angenommen, Sie arbeiten mit NumPy-Arrays

# class GetKeypoint(BaseModel):
#     NOSE:           int = 0
#     LEFT_EYE:       int = 1
#     RIGHT_EYE:      int = 2
#     LEFT_EAR:       int = 3
#     RIGHT_EAR:      int = 4
#     LEFT_SHOULDER:  int = 5
#     RIGHT_SHOULDER: int = 6
#     LEFT_ELBOW:     int = 7
#     RIGHT_ELBOW:    int = 8
#     LEFT_WRIST:     int = 9
#     RIGHT_WRIST:    int = 10
#     LEFT_HIP:       int = 11
#     RIGHT_HIP:      int = 12
#     LEFT_KNEE:      int = 13
#     RIGHT_KNEE:     int = 14
#     LEFT_ANKLE:     int = 15
#     RIGHT_ANKLE:    int = 16


class PoseKeyPoints(BaseModel):
    NOSE:           int = 0
    LEFT_EYE:       int = 1
    RIGHT_EYE:      int = 2
    LEFT_EAR:       int = 3
    RIGHT_EAR:      int = 4
    LEFT_SHOULDER:  int = 5
    RIGHT_SHOULDER: int = 6
    LEFT_ELBOW:     int = 7
    RIGHT_ELBOW:    int = 8
    LEFT_WRIST:     int = 9
    RIGHT_WRIST:    int = 10
    LEFT_HIP:       int = 11
    RIGHT_HIP:      int = 12
    LEFT_KNEE:      int = 13
    RIGHT_KNEE:     int = 14
    LEFT_ANKLE:     int = 15
    RIGHT_ANKLE:    int = 16  

class Tracker:
    def __init__(self, stop_event):
        self.stop_event = stop_event
        self.image_queue = queue.Queue()

        # Definiere die Reihenfolge, in der nach Keypoints gesucht werden soll
        self.pose_keypoints = PoseKeyPoints()
        self.priority_keypoints = [
            self.pose_keypoints.NOSE,
            (self.pose_keypoints.LEFT_EAR, self.pose_keypoints.RIGHT_EAR),
            (self.pose_keypoints.LEFT_SHOULDER, self.pose_keypoints.RIGHT_SHOULDER),
            (self.pose_keypoints.LEFT_HIP, self.pose_keypoints.RIGHT_HIP),
        ]
        return

    def update_display(self):
        while not self.image_queue.empty():
            image = self.image_queue.get()
            cv2.imshow('YOLOv8 Tracking', image)

    def find_central_point(self, keypoints):
        for kp_index in self.priority_keypoints:
            if isinstance(kp_index, tuple):  # Wenn es sich um ein Paar von Keypoints handelt
                kp_values = []
                for index in kp_index:
                    kp = keypoints[index]
                    if kp[0] > 0 or kp[1] > 0:  # Prüfe, ob die Konfidenz des Keypoints positiv ist
                        kp_values.append(kp[:2])  # Füge die X,Y-Koordinaten zur Liste hinzu
                if kp_values:  # Wenn mindestens ein Keypoint des Paares erkannt wurde
                    # Berechne den Durchschnitt der X,Y-Koordinaten
                    central_point = np.mean(kp_values, axis=0)
                    return central_point
            else:  # Für einzelne Keypoints
                kp = keypoints[kp_index]
                if kp[0] > 0 or kp[1] > 0:  # Wenn die Konfidenz des Keypoints positiv ist
                    return kp[:2]  # Gebe die X,Y-Koordinaten zurück

        return None  # Wenn kein passender Keypoint gefunden wurde



        

    def SimplifyContourMasks(self,masks):
        # Initialize an empty list to hold the simplified masks
        simplified_masks = []

        for mask in masks:
            # Reshape the mask to the correct shape (N, 1, 2) for approxPolyDP
            reshaped_mask = mask.reshape((-1, 1, 2)).astype(np.float32)  # Ensure the type matches the expected input type for cv2.approxPolyDP
            
            # Apply the Douglas-Peucker algorithm
            approx_mask = cv2.approxPolyDP(reshaped_mask, config.CONTOUR_SIMPLIFY_FACTOR, True)
            
            # Reshape the simplified mask back to (N, 2) if necessary for your application
            simplified_mask = approx_mask.reshape((-1, 2))
            
            # Add the simplified mask to the list
            simplified_masks.append(simplified_mask)

        return simplified_masks
    
    

    def triangulate_masks(self,masks):
        triangles_list = []
        for mask in masks:
            t = Triangulation(mask)
            triangles = t.triangulate_concave_polygon()
            triangles_list.append(triangles)
        return triangles_list    



    def run(self):

        fps_counter = FPSCounter()
        fps_controller = FpsController(fps=60)  # Adjust FPS as needed
        midi = MidiController.getInstance()
        webcam = WebcamInfo()


        # Load the YOLOv8 model
        if(config.WITH_SEGMENTATION):
            model = YOLO('yolov8n-seg.pt')
        elif(config.WITH_POSE):
            #model = YOLO('yolov8n.pt')
            model = YOLO('yolov8n-pose.pt')
        else:
            model = YOLO('yolov8n.pt')


        # Store the track history
        track_history = defaultdict(lambda: [])
        sender = SendTrack(webcam)
        classes = [0]  # Filter detections to class 0 (persons)
        logging.getLogger().setLevel(logging.WARNING)


        # This is a placeholder for your long-running OpenCV task
        while not self.stop_event.is_set():
            print("Background thread is running...")
            time.sleep(1)  # Simulate a task
            cap = None

            try:

                # Open the video file
                cap = cv2.VideoCapture(config.WEBCAM_IDX)
                
                #wait for hardware a moment
                time.sleep(1)


                # Loop through the video frames
                while cap.isOpened() and not self.stop_event.is_set():
                    try:
                        fps_controller.start_new_frame()
                        # Read a frame from the video
                        success, frame = cap.read()

                        fps_counter.update()
                        if success:

                            # Run YOLOv8 tracking on the frame, persisting tracks between frames
                            results = model.track(frame, persist=True,classes=classes, verbose=False,conf=0.6)

                            central_points = []
                            if(config.WITH_POSE):
                                keypoints = results[0].keypoints.xyn.cpu().numpy()
                                # Iteriere durch die Keypoints aller erkannten Personen
                                for person_keypoints in keypoints:
                                    central_points.append(self.find_central_point(person_keypoints))





                            # Visualize the results on the frame
                            annotated_frame = results[0].plot()

                            if  (results and results[0].boxes):  # Check if there are any results and any boxe
                                # Get the boxes and track IDs
                                boxes = results[0].boxes.xywh.cpu()
                                track_ids = results[0].boxes.id.int().cpu().tolist()
                                
                                #check for masks
                                masks = []
                                triangles = []
                                if results[0].masks is not None: 
                                    masks = results[0].masks.xy  # Assuming this gives a list of masks directly

                                    masks = self.SimplifyContourMasks(masks)
                                    triangles = self.triangulate_masks(masks)

                                else:
                                    # If there are no masks, initialize an empty list for each detected box
                                    masks = [[] for _ in range(len(boxes))]
                                    triangles = [[] for _ in range(len(boxes))]

                                #send messages
                                sender.send(boxes,track_ids,masks,triangles,central_points, annotated_frame)







                            # Plot the tracks
                            if results[0].boxes:
                                for box, track_id in zip(boxes, track_ids):
                                    x, y, w, h = box
                                    track = track_history[track_id]
                                    track.append((float(x), float(y)))  # x, y center point
                                    if len(track) > 30:  # retain 90 tracks for 90 frames
                                        track.pop(0)

                                    # Draw the tracking lines
                                    points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                                    cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)

                            # Display the annotated frame
                            self.image_queue.put(annotated_frame)

                        else:
                            # Break the loop if the end of the video is reached
                            break
                    except Exception as e:
                        print("===========================")
                        print( "error exception:", str(e) )
                        print("===========================")
                    finally:
                        fps_controller.wait_for_next_frame() 

                # Release the video capture object and close the display window
                cap.release()
                #cv2.destroyAllWindows()


            except Exception as e:
                print("===========================")
                print( "FATAL MAIN CAPTURE exception:", str(e) )
                print("===========================")
                time.sleep(1)
        

        del model
        torch.cuda.empty_cache()  # Clear unused memory from the cache       
        gc.collect() 
        print("EXIT TRACKER")
