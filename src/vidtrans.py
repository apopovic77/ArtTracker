import cv2
from tkinter import Tk, Scale, Button
import numpy as np

should_preview = False

def start_preview():
    global should_preview
    should_preview = True
    update_transition(preview_only=True)

def stop_preview():
    global should_preview
    should_preview = False

def update_transition(preview_only=False):
    global should_preview

    cap1 = cv2.VideoCapture('/Users/apopovic/Movies/klagenfurt boot.mov')
    cap2 = cv2.VideoCapture('/Users/apopovic/Movies/klagenfurt clouds.mov')

    initial_interval = interval_slider.get()
    total_length = length_slider.get()
    start_after = start_after_slider.get()
    decay_speed = decay_slider.get()

    time_spent = 0
    remaining_time = total_length
    current_interval = initial_interval

    current_source = cap1

    while True:
        if not should_preview and preview_only:
            break

        ret, frame = current_source.read()

        if not ret:
            break

        if time_spent < start_after:
            time_spent += initial_interval
            continue

        if remaining_time <= 0:
            break

        decay_factor = (remaining_time / total_length)**decay_speed
        current_interval = initial_interval * decay_factor

        remaining_time -= current_interval

        current_source = cap1 if current_source == cap2 else cap2

        preview = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        cv2.imshow('Transition', preview)
        cv2.waitKey(int(current_interval))

        time_spent += current_interval

    cap1.release()
    cap2.release()
    cv2.destroyAllWindows()

root = Tk()

interval_slider = Scale(root, from_=10, to=500, orient='horizontal', label='Initial Interval (ms)')
interval_slider.pack()

start_after_slider = Scale(root, from_=0, to=5000, orient='horizontal', label='Start After (ms)')
start_after_slider.pack()

length_slider = Scale(root, from_=1000, to=10000, orient='horizontal', label='Total Transition Length (ms)')
length_slider.pack()

decay_slider = Scale(root, from_=0.1, to=2, orient='horizontal', resolution=0.1, label='Decay Speed')
decay_slider.pack()

preview_button = Button(root, text="Start Preview", command=start_preview)
preview_button.pack()

stop_preview_button = Button(root, text="Stop Preview", command=stop_preview)
stop_preview_button.pack()

root.mainloop()
