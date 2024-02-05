import time
from pythonosc.udp_client import SimpleUDPClient
import threading
import queue

class OscComm:
    def __init__(self, ip, port, fps=30):
        self.client = SimpleUDPClient(ip, port)
        self.running = False
        self.thread = None
        self.message_queue = queue.Queue()
        self.lock = threading.Lock()
        self.fps = fps
        self.interval = 1.0 / fps  # Calculate interval based on FPS

    def start_client(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run)
            self.thread.start()
            print("OSC Client Started.")

    def stop_client(self):
        if self.running:
            self.running = False
            self.thread.join()  # Wait for the thread to finish
            print("OSC Client Stopped.")

    def run(self):
        while self.running:
            start_time = time.time()
            try:
                # Process messages in the queue
                with self.lock:
                    #print(str(self.message_queue.qsize())+" items in queue")
                    while not self.message_queue.empty():
                        osc_address, value = self.message_queue.get_nowait()
                        self.client.send_message(osc_address, value)
                        #print(osc_address + " value "+str(value))

                # Calculate elapsed time and adjust sleep to match FPS
                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.interval - elapsed_time)
                #print("Sleeptime "+str(sleep_time*1000)+" msec")
                time.sleep(sleep_time)
            except queue.Empty:
                continue

    def add_message(self, osc_address, value):
        with self.lock:
            self.message_queue.put((osc_address, value))
