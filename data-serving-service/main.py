from enum import Enum
from fastapi import FastAPI

from lib.influxdb_connector import InfluxdbConnector
from datetime import datetime, timedelta

app = FastAPI()

influxdb = InfluxdbConnector()

@app.get("/")
async def home():
    return { "message": "Hello World!" }


class TimeGranularity(str, Enum):
    MINUTE = "1m"
    HOUR = "1h"
    DAY = "1d"
    MONTH = "mo"

class Ticker(str, Enum):
    BTC = "BTC"
    ETH = "ETH"
    ADA = "ADA"
    SOL = "SOL"
    BNB = "BNB"
    DOGE = "DOGE"
    XRP = "XRP"

@app.get("/candlestick")
async def candlestick(
    start_datetime: datetime = datetime.now().replace(microsecond = 0) - timedelta(days = 7),
    end_datetime: datetime = datetime.now().replace(microsecond = 0),
    granularity: TimeGranularity = TimeGranularity.DAY,
    ticker: Ticker = Ticker.BTC,
):

    query = f' from(bucket: "centiment-bucket-test")\
	|> range(start: {start_datetime.isoformat()}+07:00, stop: {end_datetime.isoformat()}+07:00)\
    |> filter(fn: (r) => r["_measurement"] == "ohlc")\
    |> filter(fn: (r) => r["_field"] == "close_price" or r["_field"] == "high_price" or r["_field"] == "low_price" or r["_field"] == "open_price" or r["_field"] == "volume")\
    |> filter(fn: (r) => r["ticker"] == "{ticker}")\
    |> aggregateWindow(every: {granularity}, fn: mean)\
    |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")'

    data = influxdb.query_data(query)

    res = []
    for item in data[0].records:
        new_item = {
            "ticker": "BTC",
            "time": item["_time"],
            "low_price": item["low_price"],
            "open_price": item["open_price"],
            "volume": item["volume"],
            "close_price": item["close_price"],
            "high_price": item["high_price"]
        }
        res.append(new_item)

    return { "payload": res }