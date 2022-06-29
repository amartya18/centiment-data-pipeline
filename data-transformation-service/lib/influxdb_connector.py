import datetime
import influxdb_client

from influxdb_client import Point
from influxdb_client.client.write_api import ASYNCHRONOUS

from lib.helper import ssm_get_parameters

class InfluxdbConnector:
    BUCKET = "centiment-bucket-test"

    def __init__(self):
        token = ssm_get_parameters("influx_db_token")
        self.org = ssm_get_parameters("influx_db_org")
        url = ssm_get_parameters("influx_db_url")
        self.client = influxdb_client.InfluxDBClient(
            url = url,
            token = token,
            org = self.org,
        )

    def insert_ohlc(self, ohlc):
        data_points = []
        for item in ohlc:
            data_points.append(
                Point("ohlc")
                    .tag("ticker", item["ticker"])
                    .field("close_time", item["close_time"])
                    .field("open_price", item["open_price"])
                    .field("high_price", item["high_price"])
                    .field("low_price", item["low_price"])
                    .field("close_price", item["close_price"])
                    .field("volume", item["volume"])
            )

        print("INFLUXDB WRITE -",datetime.datetime.now())
        self.insert_data(data_points)

    def insert_tweet(self):
        pass

    def insert_data(self, point):
        write_api = self.client.write_api(write_options = ASYNCHRONOUS)
        write_api.write(bucket = self.BUCKET, org = self.org, record = point)

