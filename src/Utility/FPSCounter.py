import time

class FPSCounter:
    def __init__(self):
        self.start_time = None
        self.frame_count = 0

    def update(self):
        if self.start_time is None:
            self.start_time = time.time()

        self.frame_count += 1

    def print_fps(self):
        elapsed_time = time.time() - self.start_time
        current_fps = self.frame_count / elapsed_time
        print(f"FPS: {current_fps:.2f}")
