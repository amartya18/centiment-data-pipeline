import pickle

from lib.basic_pika_client import BasicPikaClient

class PikaProducer(BasicPikaClient):
    def declare_queue(self, queue_name):
        print(f"Trying to declare queue {queue_name}...")
        self.channel.queue_declare(queue=queue_name)

    def send_message(self, exchange, routing_key, body):
        if type(body) is dict:
            body = pickle.dumps(body)

        # TODO: check if alot of exception occurs
        try:
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=body
            )
        except Exception as err:
            print("Failed to publish tweet with error:", err)

    def close(self):
        self.channel.close()
        self.connection.close()
