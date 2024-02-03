import cv2
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk
import numpy as np


class WarpTransform:

    def __init__(self, src=None,dst=None):
        self.src = None
        self.dst = None
        if(src is not None):
            self.src = src
        if(dst is not None):
            self.dst = dst
        self.transform_matrix = None
        if(self.src is not None and self.dst is not None):
            self.transform_matrix = cv2.getPerspectiveTransform(src, dst)
    
    def transform_point(self, point):
        """
        Transforms a single point using the transformation matrix.
        """
        if(self.src is None or self.dst is None):
            return (0,0)
        pt = np.array([point[0], point[1], 1], dtype="float32")
        transformed_pt = np.dot(self.transform_matrix, pt)
        transformed_pt = transformed_pt / transformed_pt[2]
        return (int(transformed_pt[0]), int(transformed_pt[1]))
    
    def has_warp(self):
        if(self.src is not None and self.dst is not None):
            return True
        return False

class WebCamImage:
    def __init__(self, path_to_save_dir):
        self.path_to_save_dir = path_to_save_dir
        self.cap = cv2.VideoCapture(0)
        self.root = tk.Tk()
        self.root.title("Webcam Feed with Scale Adjustment")
        self.image = None
        self.saved_image_path = None  # To store the path of the saved image

    def fetch_and_update_image(self):
        ret, frame = self.cap.read()
        if ret:
            self.image = frame  # Update the global image variable

            # Resize frame according to the slider's value
            scale = self.scale_slider.get() / 100.0
            width = int(frame.shape[1] * scale)
            height = int(frame.shape[0] * scale)
            dim = (width, height)
            resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

            # Convert the frame to a format Tkinter can use
            img = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            self.panel.imgtk = imgtk
            self.panel.configure(image=imgtk)
        
        self.root.after(10, self.fetch_and_update_image)

    def save_image(self):
        if self.image is not None:
            scale = self.scale_slider.get() / 100.0
            width = int(self.image.shape[1] * scale)
            height = int(self.image.shape[0] * scale)
            resized = cv2.resize(self.image, (width, height), interpolation=cv2.INTER_AREA)

            save_path = f"{self.path_to_save_dir}/saved_frame.jpg"
            cv2.imwrite(save_path, resized)
            self.saved_image_path = save_path
            print(f"Image saved as {save_path}")

    def start_gui(self):
        self.scale_slider = tk.Scale(self.root, from_=10, to=200, orient="horizontal", label="Scale")
        self.scale_slider.set(100)  # Default scale is 50%
        self.scale_slider.pack()

        save_button = tk.Button(self.root, text="Save", command=self.save_image)
        save_button.pack()

        self.panel = tk.Label(self.root)
        self.panel.pack()



        self.fetch_and_update_image()
        self.root.mainloop()

    def Start(self):
        self.start_gui()
        self.cap.release()
        cv2.destroyAllWindows()
        return self.saved_image_path

# # Usage example
# path_to_save_dir = "/Users/apopovic/Downloads"
# wcamimage = WebCamImage(path_to_save_dir)
# path_to_final_image = wcamimage.Start()
# print(f"Final saved image path: {path_to_final_image}")
