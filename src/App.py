import tkinter as tk
import threading
import time
import cv2
from Tracker import Tracker
from configgui import ConfigGUI
import atexit
import tkinter as tk
from PIL import Image, ImageTk
import queue




class App:
    def __init__(self):
        self.background_thread = None
        self.stop_event = threading.Event()
        self.tracker = None
        

    def run_cv_tasks(self):
        self.tracker = Tracker(self.stop_event)
        self.tracker.run()

    def start(self):
        self.config_editor = ConfigGUI('config.py')
        self.config_editor.on_start.subscribe(self.on_start)
        self.config_editor.on_stop.subscribe(self.on_stop)
        self.update_display()
        self.config_editor.root.mainloop()

    def on_start(self, sender, message):
        self.stop_event.clear()
        self.background_thread = threading.Thread(target=self.run_cv_tasks, args=(), daemon=True)
        self.background_thread.start()

    def on_stop(self, sender, message):
        self.stop_event.set()
        self.background_thread.join()  # Wait for the background thread to finish

    def update_display(self):
        try:
            if( self.tracker is not None):
                self.tracker.update_display()
        finally:
            # Schedule the next update; 16 ms ~ 62.5 FPS
            self.config_editor.root.after(16, self.update_display)        

    def on_close(self):
        # Signal the background thread to stop
        self.stop_event.set()
        self.background_thread.join()  # Wait for the background thread to finish
        self.stop_event.clear()


if __name__ == "__main__":
    app = App()
    atexit.register(app.on_close)
    app.start()



