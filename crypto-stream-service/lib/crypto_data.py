import datetime
import cryptowatch as cw

from lib.helper import ssm_get_parameters
from lib.pika_producer import PikaProducer

class CryptoData:
    PIKA_QUEUE = "crypto_stream_ttl"

    def __init__(self):
        self.pika_producer = PikaProducer(
            ssm_get_parameters("rabbitmq_broker_id"),
            ssm_get_parameters("rabbitmq_user_username"),
            ssm_get_parameters("rabbitmq_user_password"),
            ssm_get_parameters("rabbitmq_broker_region"),
        )
        self.pika_producer.declare_queue(self.PIKA_QUEUE)
        cw.api_key = ssm_get_parameters("cryptowatch_public_key")


    def get_cryptocurrency_price(self, crypto):
        data = cw.markets.get(f"BINANCE-US:{crypto}USD", ohlc=True, periods=["1m"])
        ohlc = data.of_1m[-1]

        payload = {
            "ticker": crypto,
            "close_time": ohlc[0],
            "open_price": ohlc[1],
            "high_price": ohlc[2],
            "low_price": ohlc[3],
            "close_price": ohlc[4],
            "volume": ohlc[6],
        }

        return payload

    def get_all_cryptocurrency_price(self, cryptocurrencies):
        try:
            payload = []
            for crypto in cryptocurrencies:
                data = self.get_cryptocurrency_price(crypto)
                payload.append(data)

            print(datetime.datetime.now(), payload)

            self.pika_producer.send_message(
                exchange = "",
                routing_key = self.PIKA_QUEUE,
                body = payload,
            )
        except:
            # not sure if this is the right way to close the connection
            self.pika_producer.close()


