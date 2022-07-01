from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum

from lib.influxdb_connector import InfluxdbConnector
from lib.vader_sentiment import VaderSentiment

app = FastAPI()

influxdb = InfluxdbConnector()
vader_sentiment = VaderSentiment()

@app.get("/")
async def home():
    return { "message": "Hello World!" }


class TimeGranularity(str, Enum):
    MINUTE = "1m"
    FIVE_MINUTE = "5m"
    FIFTEEN_MINUTE = "15m"
    HOUR = "1h"
    DAY = "1d"
    WEEK = "7d"
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

@app.get("/tweet-volume-sentiment")
async def tweet_volume_and_sentiment(
    relative_time: RelativeTime = RelativeTime.SEVEN_DAYS,
    ticker: Ticker = Ticker.BTC,
):
    # granularity based on time_relative
    granularity = TimeGranularity.DAY
    if relative_time == RelativeTime.ONE_DAY:
        granularity = TimeGranularity.HOUR
    elif relative_time == RelativeTime.ONE_MONTH:
        granularity = TimeGranularity.WEEK

    # source aggregate: https://stackoverflow.com/questions/70291589/grouping-influx-data-per-day-using-flux
    # use timeSrc and createEmpty param in the future
    # TODO: recheck time range, timezone, and aggregateWindow timeSrc
    query = f' data = from(bucket: "centiment-bucket-test")\
	|> range(start: -{relative_time})\
    |> filter(fn: (r) => r["_measurement"] == "tweet_sentiment")\
    |> filter(fn: (r) => r["_field"] == "sentiment")\
    |> filter(fn: (r) => r["ticker"] == "{ticker}")\
    count = data\
    |> aggregateWindow(every: {granularity}, fn: count)\
    mean = data\
    |> aggregateWindow(every: {granularity}, fn: mean)\
    join(\
        tables: {{count:count, mean:mean}},\
        on: ["_time", "_stop", "_start", "ticker"],\
    )'

    data = influxdb.query_data(query)

    res = []
    for item in data[0].records:
        if item["_value_mean"] >= 45 and item["_value_mean"] <= 55:
            tweet_sentiment = "neutral"
        elif item["_value_mean"] < 45:
            tweet_sentiment = "negative"
        elif item["_value_mean"] > 55:
            tweet_sentiment = "positive"

        new_item = {
            "ticker": item["ticker"],
            "time": item["_time"],
            "tweet_volume": item["_value_count"],
            "tweet_sentiment": {
                "score": item["_value_mean"],
                "polarity": tweet_sentiment,
            }
        }
        res.append(new_item)

    return { "payload" : res }

@app.get("/coin-sentiment-comparison")
async def coin_sentiment_comparison(
    relative_time: RelativeTime = RelativeTime.SEVEN_DAYS,
):

    query = f' from(bucket: "centiment-bucket-test")\
	|> range(start: -{relative_time})\
    |> filter(fn: (r) => r["_measurement"] == "tweet_sentiment")\
    |> filter(fn: (r) => r["_field"] == "sentiment")\
    |> mean()'

    data = influxdb.query_data(query)

    res = []
    for table in data:
        for item in table.records:
            print(item)
            new_item = {
                "ticker": item["ticker"],
                "tweet_sentiment": item["_value"]
            }
            res.append(new_item)

    return { "payload" : res }

class TwitteSentimentTestText(BaseModel):
    text: str

@app.post("/twitter-sentiment-test")
async def twitter_sentiment_test(
    text: TwitteSentimentTestText
):
    res = vader_sentiment.get_polarity(text.text)

    return { "payload" : res }