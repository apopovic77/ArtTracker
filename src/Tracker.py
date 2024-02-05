from collections import defaultdict
from protobuf.TrackedPerson_pb2 import TrackedPerson
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime
import sys
import os
import config
from Utility.FPSCounter import FPSCounter
fps_counter = FPSCounter()
from FpsController import FpsController

fps_controller = FpsController(fps=60)  # Adjust FPS as needed

from Midi.MidiController import MidiController
midi = MidiController.getInstance()
#midi.start_keyboard_listener()


from Utility.WebcamInfo import WebcamInfo
webcam = WebcamInfo()

import cv2
import numpy as np
import time
from ultralytics import YOLO

from SendTrack import SendTrack

# Load the YOLOv8 model
model = YOLO('yolov8n.pt')

# Open the video file
cap = cv2.VideoCapture(0)
time.sleep(1)

# Store the track history
track_history = defaultdict(lambda: [])

#config
sender = SendTrack(webcam)
classes = [0]  # Filter detections to class 0 (persons)

import logging
logging.getLogger().setLevel(logging.WARNING)




# Loop through the video frames
while cap.isOpened():
    try:
        fps_controller.start_new_frame()
        # Read a frame from the video
        success, frame = cap.read()

        fps_counter.update()
        if success:


            # Run YOLOv8 tracking on the frame, persisting tracks between frames
            results = model.track(frame, persist=True,classes=classes, verbose=False,conf=0.6)



            if not (results and results[0].boxes):  # Check if there are any results and any boxe
                continue

            # Get the boxes and track IDs
            boxes = results[0].boxes.xywh.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()


            # Visualize the results on the frame
            annotated_frame = results[0].plot()

            #send messages
            sender.send(boxes,track_ids, annotated_frame)






            # Plot the tracks
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
            cv2.imshow("YOLOv8 Tracking", annotated_frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
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
cv2.destroyAllWindows()