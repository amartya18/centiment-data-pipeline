from lib.basic_pika_client import BasicPikaClient

class PikaConsumer(BasicPikaClient):
    def consume_messages(self, exchange, queue, callback):
        self.check_connection_and_channel(exchange, queue)

        self.channel.basic_consume(queue = queue, on_message_callback = callback, auto_ack = True)

        print(' [*] Consumer started. To exit press CTRL+C')
        self.channel.start_consuming()

    def close(self):
        self.channel.close()
        self.connection.close()
