import cv2
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

from collections import defaultdict
import numpy as np

track_history = defaultdict(lambda: [])

model = YOLO("yolov8n-seg.pt")   # segmentation model
cap = cv2.VideoCapture(0)
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

#out = cv2.VideoWriter('instance-segmentation-object-tracking.avi', cv2.VideoWriter_fourcc(*'MJPG'), fps, (w, h))

while True:
    ret, im0 = cap.read()
    if not ret:
        print("Video frame is empty or video processing has been successfully completed.")
        break

    annotator = Annotator(im0, line_width=2)

    results = model.track(im0, persist=True, classes=[0])

    if results[0].boxes.id is not None and results[0].masks is not None:
        masks = results[0].masks.xy
        track_ids = results[0].boxes.id.int().cpu().tolist()

        for mask, track_id in zip(masks, track_ids):
            #print(mask)
            mask_np = np.array(mask, dtype=np.int32)
            cv2.polylines(im0, [mask_np],False,(255,90,0),1)
            # annotator.seg_bbox(mask=mask,
            #                    mask_color=colors(track_id, True),
            #                    track_label=str(track_id))

    #out.write(im0)
    cv2.imshow("instance-segmentation-object-tracking", im0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#out.release()
cap.release()
cv2.destroyAllWindows()