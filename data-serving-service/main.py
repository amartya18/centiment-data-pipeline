from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum

from lib.influxdb_connector import InfluxdbConnector
from lib.vader_sentiment import VaderSentiment

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    TWO_DAYS = "2d"
    WEEK = "7d"
    TWO_WEEKS = "14d"
    MONTH = "mo"
    TWO_MONTHS = "2mo"

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
            "ticker": item["ticker"],
            "time": item["_time"],
            "low_price": item["low_price"],
            "open_price": item["open_price"],
            "close_price": item["close_price"],
            "high_price": item["high_price"]
        }
        res.append(new_item)

    return { "code": 200, "payload": res }

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
        granularity = TimeGranularity.MINUTE
    elif relative_time == RelativeTime.ONE_MONTH:
        granularity = TimeGranularity.MONTH

    query = f''' 
        data = from(bucket: "centiment-bucket-test")
            |> range(start: -{relative_time})
            |> filter(fn: (r) => r["_measurement"] == "ohlc")
            |> filter(fn: (r) => r["ticker"] == "{ticker}")

            open = data 
                |> filter(fn: (r) => r["_field"] == "open_price")
                |> aggregateWindow(every: {granularity}, fn: first)

            close = data 
                |> filter(fn: (r) => r["_field"] == "close_price")
                |> aggregateWindow(every: {granularity}, fn: last)

            high = data 
                |> filter(fn: (r) => r["_field"] == "high_price")
                |> aggregateWindow(every: {granularity}, fn: max)

            low = data 
                |> filter(fn: (r) => r["_field"] == "low_price")
                |> aggregateWindow(every: {granularity}, fn: min)
            
            first_join = join(
                tables: {{open:open, close:close}},
                on: ["_start", "_stop", "_time", "_measurement", "ticker"],
            )
            first_join
            second_join = join(
                tables: {{high:high, low:low}},
                on: ["_start", "_stop", "_time", "_measurement", "ticker"],
            )

            join(
                tables: {{first:first_join, second:second_join}},
                on: ["_start", "_stop", "_time", "_measurement", "ticker"],
            )
    '''


    data = influxdb.query_data(query)

    res = []
    for item in data[0].records:
        new_item = {
            "ticker": item["ticker"],
            "time": item["_time"],
            "low_price": replaceNullWithZero(item["_value_low"]),
            "open_price": replaceNullWithZero(item["_value_open"]),
            "close_price": replaceNullWithZero(item["_value_close"]),
            "high_price": replaceNullWithZero(item["_value_high"])
        }
        res.append(new_item)

    return { "code": 200, "payload": res }

# TODO: if null error bcs of converting
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
        try:
            if item["_value_mean"] <= 50:
                tweet_sentiment = "negative"
            elif item["_value_mean"] > 50:
                tweet_sentiment = "positive"
        except:
            tweet_sentiment = ""

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

    return { "code": 200, "payload": res }

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
            new_item = {
                "ticker": item["ticker"],
                "tweet_sentiment": item["_value"]
            }
            res.append(new_item)

    return { "code": 200, "payload": res }

class TwitteSentimentTestText(BaseModel):
    text: str

@app.post("/twitter-sentiment-test")
async def twitter_sentiment_test(
    text: TwitteSentimentTestText
):
    res = vader_sentiment.get_polarity(text.text)

    return { "code": 200, "payload": res }

@app.get("/tweet-trade-correlation")
async def tweet_trade_correlation(
    relative_time: RelativeTime = RelativeTime.SEVEN_DAYS,
    ticker: Ticker = Ticker.BTC,
):
    # granularity based on time_relative
    granularity = TimeGranularity.DAY
    if relative_time == RelativeTime.ONE_DAY:
        granularity = TimeGranularity.HOUR
    elif relative_time == RelativeTime.ONE_MONTH:
        granularity = TimeGranularity.WEEK

    query = f' trade_volume = from(bucket: "centiment-bucket-test")\
	|> range(start: -{relative_time})\
    |> filter(fn: (r) => r["_measurement"] == "ohlc")\
    |> filter(fn: (r) => r["_field"] == "volume")\
    |> filter(fn: (r) => r["ticker"] == "{ticker}")\
    |> aggregateWindow(every: {granularity}, fn: mean)\
    trade_volume_max = trade_volume\
    |> max()\
    |> findColumn(\
        fn: (key) => key._field == "volume",\
        column: "_value",\
    )\
    trade_volume_percentage = trade_volume\
    |> map(\
        fn: (r) => ({{\
            _time: r._time,\
            _measurement: r._measurement,\
            _field: "trade_volume_percent",\
            _value: float(v: r._value) / float(v: trade_volume_max[0]) * 100.0\
        }}),\
    )\
    tweet_volume = from(bucket: "centiment-bucket-test")\
	|> range(start: -{relative_time})\
    |> filter(fn: (r) => r["_measurement"] == "tweet_sentiment")\
    |> filter(fn: (r) => r["_field"] == "sentiment")\
    |> filter(fn: (r) => r["ticker"] == "{ticker}")\
    |> aggregateWindow(every: {granularity}, fn: count)\
    tweet_volume_max = tweet_volume\
    |> max()\
    |> findColumn(\
        fn: (key) => key._field == "sentiment",\
        column: "_value",\
    )\
    tweet_volume_percentage = tweet_volume\
    |> map(\
        fn: (r) => ({{\
            _time: r._time,\
            _measurement: r._measurement,\
            _field: "tweet_volume_percent",\
            _value: float(v: r._value) / float(v: tweet_volume_max[0]) * 100.0\
        }}),\
    )\
    join(\
        tables: {{trade:trade_volume_percentage, tweet:tweet_volume_percentage}},\
        on: ["_time"],\
    )'

    data = influxdb.query_data(query)

    res = []
    for item in data[0].records:
        new_item = {
            "ticker": ticker,
            "time": item["_time"],
            "trade_volume_percentage": item["_value_trade"],
            "tweet_volume_percentage": item["_value_tweet"],
        }
        res.append(new_item)


    return { "code": 200, "payload": res }

@app.get("/coin-general-information")
async def coin_general_information(
    ticker: Ticker = Ticker.BTC,
):

    query = f'''
        price_after = from(bucket: "centiment-bucket-test")
            |> range(start: -1d)
            |> filter(fn: (r) => r["_measurement"] == "ohlc")
            |> filter(fn: (r) => r["_field"] == "open_price")
            |> filter(fn: (r) => r["ticker"] == "{ticker}")
            |> last()
        price_before = from(bucket: "centiment-bucket-test")
            |> range(start: -2d, stop: -1d)
            |> filter(fn: (r) => r["_measurement"] == "ohlc")
            |> filter(fn: (r) => r["_field"] == "open_price")
            |> filter(fn: (r) => r["ticker"] == "{ticker}")
            |> last()
        trade_price = join(
                tables: {{after:price_after, before:price_before}},
                on: ["_field", "ticker"],
            )
                |> map(fn: (r) => ({{r with _value: (r._value_after - r._value_before) * 100.0 / r._value_before}}))

        volume_after = from(bucket: "centiment-bucket-test")
            |> range(start: -1d)
            |> filter(fn: (r) => r["_measurement"] == "ohlc")
            |> filter(fn: (r) => r["_field"] == "volume")
            |> filter(fn: (r) => r["ticker"] == "{ticker}")
            |> sum()
        volume_before = from(bucket: "centiment-bucket-test")
            |> range(start: -2d, stop: -1d)
            |> filter(fn: (r) => r["_measurement"] == "ohlc")
            |> filter(fn: (r) => r["_field"] == "volume")
            |> filter(fn: (r) => r["ticker"] == "{ticker}")
            |> sum()
        trade_volume = join(
            tables: {{after:volume_after, before:volume_before}},
            on: ["_field", "ticker"],
        )

            |> map(fn: (r) => ({{r with _value: (r._value_after - r._value_before) * 100.0 / r._value_before}}))
        sentiment_before = from(bucket: "centiment-bucket-test")
            |> range(start: -1d)
            |> filter(fn: (r) => r["_measurement"] == "tweet_sentiment")
            |> filter(fn: (r) => r["_field"] == "sentiment")
            |> filter(fn: (r) => r["ticker"] == "{ticker}")
            |> mean()
        sentiment_after = from(bucket: "centiment-bucket-test")
            |> range(start: -2d, stop: -1d)
            |> filter(fn: (r) => r["_measurement"] == "tweet_sentiment")
            |> filter(fn: (r) => r["_field"] == "sentiment")
            |> filter(fn: (r) => r["ticker"] == "{ticker}")
            |> mean()
        tweet_sentiment = join(
            tables: {{after:sentiment_after, before:sentiment_before}},
            on: ["_field", "ticker"],
        )

            |> map(fn: (r) => ({{r with _value: (r._value_after - r._value_before) * 100.0 / r._value_before}}))
        count_before = from(bucket: "centiment-bucket-test")
            |> range(start: -1d)
            |> filter(fn: (r) => r["_measurement"] == "tweet_sentiment")
            |> filter(fn: (r) => r["_field"] == "sentiment")
            |> filter(fn: (r) => r["ticker"] == "{ticker}")
            |> count()
        count_after = from(bucket: "centiment-bucket-test")
            |> range(start: -2d, stop: -1d)
            |> filter(fn: (r) => r["_measurement"] == "tweet_sentiment")
            |> filter(fn: (r) => r["_field"] == "sentiment")
            |> filter(fn: (r) => r["ticker"] == "{ticker}")
            |> count()
        tweet_count = join(
            tables: {{after:count_after, before:count_before}},
            on: ["_field", "ticker"],
        )
            |> map(fn: (r) => ({{r with _value: (float(v: r._value_after) - float(v: r._value_before)) * 100.0 / float(v: r._value_before)}}))

        first_join = join(
            tables: {{trade_price:trade_price, trade_volume:trade_volume}},
            on: ["ticker"],
        )
        second_join = join(
            tables: {{tweet_sentiment:tweet_sentiment, tweet_count:tweet_count}},
            on: ["ticker"],
        )

        join(
            tables: {{first:first_join, second:second_join}},
            on: ["ticker"],
        )
    '''

    data = influxdb.query_data(query)

    item = data[0].records[0]
    res = {
        "ticker": ticker,
        "coin_price": round(item["_value_after_trade_price"], 3),
        "coin_volume": round(item["_value_after_trade_volume"], 2),
        "tweet_count": item["_value_after_tweet_count"],
        "tweet_sentiment": round(item["_value_after_tweet_sentiment"], 2),
        "coin_price_percentage": round(item["_value_trade_price"], 2),
        "coin_volume_percentage": round(item["_value_trade_volume"], 2),
        "tweet_count_percentage": round(item["_value_tweet_count"], 2),
        "tweet_sentiment_percentage": round(item["_value_tweet_sentiment"], 2),
    }

    return { "code": 200, "payload": res }

@app.get("/all-coin-information")
async def all_coin_information():
    res = []
    for item in Ticker:
        coin = await coin_general_information(item.value)
        res.append(coin["payload"])

    return { "code": 200, "payload": res }

@app.get("/twitter-fear-greed")
async def twitter_fear_greed(
    ticker: Ticker = Ticker.BTC,
):
    query = f'''
        now = from(bucket: "centiment-bucket-test")
            |> range(start: -1d)
            |> filter(fn: (r) => r["_measurement"] == "tweet_sentiment")
            |> filter(fn: (r) => r["_field"] == "sentiment")
            |> filter(fn: (r) => r["ticker"] == "{ticker}")
            |> mean()

        yesterday = from(bucket: "centiment-bucket-test")
            |> range(start: -2d, stop: -1d)
            |> filter(fn: (r) => r["_measurement"] == "tweet_sentiment")
            |> filter(fn: (r) => r["_field"] == "sentiment")
            |> filter(fn: (r) => r["ticker"] == "{ticker}")
            |> mean()

        last_week = from(bucket: "centiment-bucket-test")
            |> range(start: -7d)
            |> filter(fn: (r) => r["_measurement"] == "tweet_sentiment")
            |> filter(fn: (r) => r["_field"] == "sentiment")
            |> filter(fn: (r) => r["ticker"] == "{ticker}")
            |> mean()

        last_month = from(bucket: "centiment-bucket-test")
            |> range(start: -1mo)
            |> filter(fn: (r) => r["_measurement"] == "tweet_sentiment")
            |> filter(fn: (r) => r["_field"] == "sentiment")
            |> filter(fn: (r) => r["ticker"] == "{ticker}")
            |> mean()

        first_join = join(
            tables: {{now:now, yesterday:yesterday}},
            on: ["ticker", "_field", "_measurement"],
        )

        second_join = join(
            tables: {{last_week:last_week, last_month:last_month}},
            on: ["ticker", "_field", "_measurement"],
        )

        join(
            tables: {{first:first_join, second:second_join}},
            on: ["ticker", "_field", "_measurement"],
        )
    '''

    data = influxdb.query_data(query)

    res = []
    for item in data[0].records:
        new_item = {
            "ticker": item["ticker"],
            "last_month": int(item["_value_last_month"]),
            "last_week": int(item["_value_last_week"]),
            "now": int(item["_value_now"]),
            "yesterday": int(item["_value_yesterday"]),
        }
        res.append(new_item)

    return { "code": 200, "payload": res }

@app.get("/tweet-trending-coins")
async def tweet_trending_coins():
    query = f'''
        from(bucket: "centiment-bucket-test")
            |> range(start: -8d, stop: -1d)
            |> filter(fn: (r) => r["_measurement"] == "tweet_sentiment")
            |> filter(fn: (r) => r["_field"] == "sentiment")
            |> aggregateWindow(every: 1d, fn: count)
            |> mean()
    '''

    data_comparison = influxdb.query_data(query)

    tweet_volume_comparison = []
    for table in data_comparison:
        for item in table.records:
            new_item = {
                "ticker": item["ticker"],
                "tweet_volume": item["_value"]
            }
            tweet_volume_comparison.append(new_item)

    query = f'''
        from(bucket: "centiment-bucket-test")
            |> range(start: -1d)
            |> filter(fn: (r) => r["_measurement"] == "tweet_sentiment")
            |> filter(fn: (r) => r["_field"] == "sentiment")
            |> count()
    '''

    data = influxdb.query_data(query)

    tweet_volume= []
    for table in data:
        for item in table.records:
            new_item = {
                "ticker": item["ticker"],
                "tweet_volume": item["_value"]
            }
            tweet_volume.append(new_item)

    combined_tweet_volume = []
    for tweet_today in tweet_volume:
        for tweet_comparison in tweet_volume_comparison:
            if tweet_today["ticker"] == tweet_comparison["ticker"]:
                combined_tweet_volume.append({
                    "ticker": tweet_today["ticker"],
                    "tweet_volume_now": int(tweet_today["tweet_volume"]),
                    "tweet_volume_before": int(tweet_comparison["tweet_volume"]),
                    "percentage": int((tweet_today["tweet_volume"] - tweet_comparison["tweet_volume"]) * 100 / tweet_comparison["tweet_volume"]),
                })

    res = sorted(combined_tweet_volume, key = lambda x: x["percentage"], reverse = True)[:-4]

    return { "code": 200, "payload": res }

@app.get("/recent-tweets-sentiment")
async def recent_tweets_sentiment():
    query = '''
        from(bucket: "centiment-bucket-test")
            |> range(start: -5m)
            |> filter(fn: (r) => r["_measurement"] == "tweet_sentiment")
            |> filter(fn: (r) => r["_field"] == "name" or r["_field"] == "sentiment" or r["_field"] == "tweet" or r["_field"] == "username" or r["_field"] == "tweet_id")
            |> pivot(rowKey: ["_time", "_start", "_stop", "_measurement"], columnKey: ["_field"], valueColumn: "_value")
    '''

    data = influxdb.query_data(query)

    tweets = []
    for table in data:
        for item in table.records:
            tweets.append({
                "ticker": item["ticker"],
                "username": item["username"],
                "name": item["name"],
                "tweet": item["tweet"],
                "tweet_id": item["tweet_id"],
                "time": item["_time"],
                "sentiment": item["sentiment"],
            })

    tweets.sort(key=lambda x: x["time"], reverse = True)

    return { "code": 200, "payload": tweets }

def replaceNullWithZero(num):
    if num == None:
        return 0
    else:
        return num