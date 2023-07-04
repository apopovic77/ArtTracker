import socketserver
import threading
import struct
import time
from google.protobuf.timestamp_pb2 import Timestamp
from TrackedPerson_pb2 import TrackedPerson
from queue import Queue

requests = []

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        
        request_type = type(self.request)
        print("Type of self.request:", request_type)
        
        print("new client")
        TcpServer.instance().add_request(self.request)
        
        while True:
            time.sleep(0.5)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class TcpServer:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self ):
        self.lock = threading.Lock()
        self.server = None
        self.requests = []
        self.current_tracks = []
        self.sender_thread = None
        self.server_thread = None
        self.HOST, self.PORT = '172.20.10.4', 5554

    def LOCK(self):
        #print("LOCK")
        self.lock.acquire()
    
    def UNLOCK(self):
        #print("UNLOCK")
        self.lock.release()

    def add_request(self, request):
        self.LOCK()
        requests.append(request)        
        self.UNLOCK()

    def Run(self):
        self.server_thread = threading.Thread(target=self._dorun)
        self.server_thread.daemon = True
        self.server_thread.start()

        self.sender_thread = threading.Thread(target=self.send_data)
        self.sender_thread.daemon = True
        self.sender_thread.start()

    def _dorun(self):
        self.server = ThreadedTCPServer((self.HOST, self.PORT), ThreadedTCPRequestHandler)
        print(f"Server is running on {self.HOST}:{self.PORT}")
        self.server.serve_forever()

    def add_persons(self, tracks):
        self.LOCK()
        self.current_tracks = tracks
        self.UNLOCK()

    def send_data(self):
        while True:
            self.LOCK()
            tracks_to_send = self.current_tracks.copy()
            curr_destinations = requests.copy()
            self.UNLOCK()

            for track in tracks_to_send:
                if(track is None):
                    continue
                timestamp = track.timestamp.ToDatetime()
                timestamp_ms = int(timestamp.timestamp() * 1000)
                data = struct.pack('>iddddq', track.id, track.boundingbox.x, track.boundingbox.y, track.boundingbox.width, track.boundingbox.height, timestamp_ms)
                for dest in curr_destinations:
                    if dest is None:
                        continue
                    try:
                        dest.sendall(data)
                    except (BrokenPipeError, ConnectionResetError):
                        self.LOCK()
                        print("CLIENT DISCONNECTED")
                        requests.remove(dest)
                        self.UNLOCK()

            time.sleep(60/1000) # send data every second
