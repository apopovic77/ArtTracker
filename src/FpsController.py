import time

class FpsController:
    def __init__(self, fps):
        self.fps = fps
        self.interval = 1.0 / fps
        self.start_time = time.time()

    def start_new_frame(self):
        """Call this method at the beginning of each frame."""
        self.start_time = time.time()

    def wait_for_next_frame(self):
        """Call this method at the end of each frame to wait for the next frame."""
        elapsed_time = time.time() - self.start_time
        sleep_time = max(0, self.interval - elapsed_time)
        # Uncomment the next line to print sleep time for debugging
        # print("Sleep time: {:.2f} ms".format(sleep_time * 1000))
        time.sleep(sleep_time)
