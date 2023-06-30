import pika

class RabbitMessageBroker:
    _connection = None
    _channel = None

    @classmethod
    def get_connection(cls):
        if cls._connection is None or not cls._connection.is_open:
            cls._connection = cls._create_connection()
        return cls._connection
    
    @classmethod
    def get_channel(cls):
        if cls._channel is None:
            cls._channel = cls.get_connection().channel()
            cls._channel.queue_declare(queue='task_queue', durable=True)
            cls._channel.queue_purge(queue='task_queue')
        return cls._channel

    @classmethod
    def _create_connection(cls):
        credentials = pika.PlainCredentials('admin', '#1Inetpass')
        parameters = pika.ConnectionParameters('172.20.10.2', credentials=credentials)
        connection = pika.BlockingConnection(parameters)
        return connection

    @classmethod
    def send_to_shared_mem(cls, track):
        cls.get_channel().basic_publish(
            exchange='',
            routing_key='task_queue',
            body=track.SerializeToString(),
            properties=pika.BasicProperties(delivery_mode=2)
        )
