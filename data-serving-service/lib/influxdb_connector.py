import influxdb_client

import dateutil.parser
from dateutil.tz import gettz

from influxdb_client.client.util import date_utils
from influxdb_client.client.util.date_utils import DateHelper

from lib.helper import ssm_get_parameters

def parse_date(date_string: str):
    return dateutil.parser.parse(date_string).astimezone(gettz("Asia/Jakarta"))

date_utils.date_helper = DateHelper()
date_utils.date_helper.parse_date = parse_date

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
        self.query_api = self.client.query_api()

    def query_data(self, query):
        return self.query_api.query(org = self.org, query = query)

