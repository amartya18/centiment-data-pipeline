import json

from lib.pika_consumer import PikaConsumer
from lib.influxdb_connector import InfluxdbConnector
from lib.helper import ssm_get_parameters

class Ohlc:
    def __init__(self):
        self.influxdb_connector = InfluxdbConnector()

    def process_data(self,ch, method, properties, body):
        self.influxdb_connector.insert_ohlc(json.loads(body))

if __name__ == "__main__":
    ohlc = Ohlc()

    basic_message_receiver = PikaConsumer(
        ssm_get_parameters("rabbitmq_broker_id"),
        ssm_get_parameters("rabbitmq_user_username"),
        ssm_get_parameters("rabbitmq_user_password"),
        ssm_get_parameters("rabbitmq_broker_region"),
        exchange = "ohlc",
        queue = "ohlc-consumer",
    )

    # temporarily test
    # try:
    basic_message_receiver.consume_messages("ohlc", "ohlc-consumer", ohlc.process_data)

    # except:
    #     basic_message_receiver.close()