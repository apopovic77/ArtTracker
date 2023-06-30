# server.py
import zmq
import threading


# Create a lock object
lock = threading.Lock()

class PubService():
    def __init__(self):
        self.server = None
        #self.server_thread = threading.Thread(target=self.serve)
        self.port = 5556
        context = zmq.Context()
        context.setsockopt(zmq.SNDBUF, 10 * 1024 * 1024)
        self.socket = context.socket(zmq.PUB)
        
    def send(self, topic ,msgobj):
        # # Acquire the lock before accessing the shared queue
        # lock.acquire()
        try:
            self.socket.send_multipart([topic.encode(), msgobj.SerializeToString()])
        except Exception as e:
            print("===========================")
            print( "StreamData:", str(e) )
            print("===========================")
        finally:
            # Release the lock after accessing the queue
            # lock.release()
        

    # def serve(self):
    #     self.socket.bind("tcp://*:%s" % self.port)
    #     #self.server_thread.join()
        

    def run_server(self):
        self.socket.bind("tcp://*:%s" % self.port)
        #self.server_thread.start()


