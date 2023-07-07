
import cv2
import threading
import time

class VideoPlayer:
    def __init__(self):
        self.cap = None
        self.current_area = None
        self.frame = None
        self.update_frame = False
        self.play_thread = None

    def play_video_for_area(self, current_area):
        # Define the video file paths for each area

        video_paths = {
            1: '/Users/apopovic/Downloads/Boy_christopher_playground 01.MP4',
            2: '/Users/apopovic/Downloads/Woman_Christopher_Radio_01.MP4',
            3: '/Users/apopovic/Downloads/Woman_christopher_Bar_01.MP4',
            4: '/Users/apopovic/Downloads/Woman_Bar_Amber_01.MP4'
        }

        # Check if the area is the same as before
        if current_area == self.current_area:
            # Continue playing the active video
            return

        # Check if the video file path exists for the current area
        video_path = video_paths.get(current_area)
        if video_path is None:
            print(f"No video file found for area {current_area}")
            return

        # Stop the previous playback thread if any
        self.stop_playback()

        # Release the previous video capture if any
        if self.cap is not None:
            self.cap.release()

        # Load the video for the current area
        self.cap = cv2.VideoCapture(video_path)

        # Check if the video is successfully loaded
        if not self.cap.isOpened():
            print(f"Failed to open video file for area {current_area}")
            return

        self.current_area = current_area

        # Start a new playback thread
        self.play_thread = threading.Thread(target=self.play_video)
        self.play_thread.start()

    def play_video(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Update the frame to be displayed
                self.frame = frame
                self.update_frame = True

                # Wait for the main thread to display the frame
                while self.update_frame:
                    time.sleep(0.01)
            else:
                # End of video, break the loop
                break

        # Release the video capture and close windows
        self.cap.release()
        cv2.destroyAllWindows()

    def display_frame(self):
        # while True:
            if self.frame is not None and self.update_frame:
                # Display the frame in the main thread
                cv2.imshow(f"Area {self.current_area} Video", self.frame)

                self.update_frame = True

            #time.sleep(0.01)

    def stop_playback(self):
        if self.play_thread is not None and self.play_thread.is_alive():
            # Release the video capture and wait for the playback thread to finish
            self.cap.release()
            self.play_thread.join()

    def release(self):
        self.stop_playback()
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
