import ssl
import pika

class BasicPikaClient:
    def __init__(self, rabbitmq_broker_id, rabbitmq_user, rabbitmq_password, region, exchange):
        # SSL Context for TLS configuration of Amazon MQ for RabbitMQ
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_context.set_ciphers('ECDHE+AESGCM:!ECDSA')

        url = f"amqps://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_broker_id}.mq.{region}.amazonaws.com:5671"
        self.parameters = pika.URLParameters(url)
        self.parameters.ssl_options = pika.SSLOptions(context=ssl_context)

        self.reconnect(self.parameters, exchange)

    def reconnect(self, parameters, exchange):
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        # change to pubsub
        self.channel.exchange_declare(exchange = exchange, exchange_type = "fanout")

    def check_connection_and_channel(self, exchange):
        # source: https://stackoverflow.com/questions/56322608/allow-rabbitmq-and-pika-maintain-the-conection-always-open
        if not self.connection or self.connection.is_closed:
            print("connection closed...")
            self.reconnect(self.parameters)
        elif self.channel.is_closed:
            print("channel closed...")
            self.channel = self.connection.channel()
            # change to pubsub
            self.channel.exchange_declare(exchange = exchange, exchange_type = "fanout")
