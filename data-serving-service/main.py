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
    FIVE_MINUTE = "5m"
    FIFTEEN_MINUTE = "15m"
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
    |> filter(fn: (r) => r["_field"] == "close_price" or r["_field"] == "high_price" or r["_field"] == "low_price" or r["_field"] == "open_price")\
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
            "close_price": item["close_price"],
            "high_price": item["high_price"]
        }
        res.append(new_item)

    return { "payload": res }

class RelativeTime(str, Enum):
    ONE_DAY = "1d"
    SEVEN_DAYS = "7d"
    ONE_MONTH = "1mo"

@app.get("/candlestick-relative")
async def candlestick_relative(
    relative_time: RelativeTime = RelativeTime.SEVEN_DAYS,
    ticker: Ticker = Ticker.BTC,
):

    # granularity based on time_relative
    granularity = TimeGranularity.HOUR

    if relative_time == RelativeTime.ONE_DAY:
        granularity = TimeGranularity.FIVE_MINUTE
    elif relative_time == RelativeTime.ONE_MONTH:
        granularity = TimeGranularity.MONTH

    query = f' from(bucket: "centiment-bucket-test")\
	|> range(start: -{relative_time})\
    |> filter(fn: (r) => r["_measurement"] == "ohlc")\
    |> filter(fn: (r) => r["_field"] == "close_price" or r["_field"] == "high_price" or r["_field"] == "low_price" or r["_field"] == "open_price")\
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
            "close_price": item["close_price"],
            "high_price": item["high_price"]
        }
        res.append(new_item)

    return { "payload": res }
