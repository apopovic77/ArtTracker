import pika

class MessageConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None

    def connect(self):
        credentials = pika.PlainCredentials('admin', '#1Inetpass')
        parameters = pika.ConnectionParameters('172.20.10.2', credentials=credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='task_queue', durable=True)
        self.channel.basic_qos(prefetch_count=1)

    def consume_messages(self):
        self.channel.basic_consume(queue='task_queue', on_message_callback=self.handle_message, auto_ack=True)
        self.channel.start_consuming()

    def handle_message(self, channel, method, properties, body):
        print(f"Received message: {body}")

if __name__ == '__main__':
    consumer = MessageConsumer()
    consumer.connect()
    consumer.consume_messages()