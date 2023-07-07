# client.py
# FOR THIS TO RUN START RABBITMQ    with
# ============================
# brew services start rabbitmq

# needs to be done when exposing rabbitmq to an external port
#rabbitmqctl add_user <username> <password>
#rabbitmqctl set_user_tags <username> administrator
#rabbitmqctl set_permissions -p / <username> ".*" ".*" ".*"
# ============================


import zmq
from protobuf.TrackedPerson_pb2 import TrackedPerson,BoundingBox


from Utility.FPSCounter import FPSCounter
fps_counter = FPSCounter()

from Utility.Logger import Logger
logger = Logger()
logger.set_log_file("test.txt")
logger.disable_console_logging()
logger.disable_file_logging()

from TestTrackerClient import ConsoleRenderer
console_renderer = ConsoleRenderer()



class SubClient():
    def __init__(self, topics=None):
        self.port = 5556
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)

        # Connect to the server
        self.socket.connect("tcp://172.20.10.2:%s" % self.port)

        # Subscribe to all topics if no specific topics are given
        if not topics:
            self.socket.setsockopt_string(zmq.SUBSCRIBE, '')
        else:
            for topic in topics:
                self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)

    def receive(self):
        while True:
            try:

                fps_counter.update()
                # Receive a topic and message
                topic, msg = self.socket.recv_multipart()
                logger.log_info("Received topic: " +topic.decode())

                # Deserialize the message
                tracked_person = TrackedPerson()
                tracked_person.ParseFromString(msg)

                #use shared mem to share
                #SendToSharedMem(tracked_person)

                console_renderer.set_position(1-(tracked_person.boundingbox.x+tracked_person.boundingbox.width/2))
                
                fps_counter.print_fps()
            except zmq.ZMQError as e:
                logger.log_error("ZMQError: ", e)
            except Exception as e:
                logger.log_error("Exception: ", e)

if __name__ == "__main__":
    console_renderer.start()
    client = SubClient()
    client.receive()
