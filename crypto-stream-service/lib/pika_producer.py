import json

from lib.basic_pika_client import BasicPikaClient

class PikaProducer(BasicPikaClient):
    def send_message(self, exchange, body):
        self.check_connection_and_channel(exchange = exchange)

        if type(body) is dict or list:
            body = json.dumps(body)

        try:
            self.channel.basic_publish(
                exchange = exchange,
                routing_key = "",
                body = body
            )
        except Exception as err:
            print("Failed to publish crypto data with error:", err)

    def close(self):
        self.channel.close()
        self.connection.close()
