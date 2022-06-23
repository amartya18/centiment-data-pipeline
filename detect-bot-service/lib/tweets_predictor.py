from ratelimit import RateLimitException

from lib.helper import ssm_get_parameters
from lib.btmtr import Btmtr
from lib.bot_redis import BotRedis
from lib.pika_producer import PikaProducer

class TweetsPredictor:
    # not using botometer lite because accuracy disapointing
    PIKA_QUEUE = "twitter_stream_test"

    def __init__(self):
        self.btmtr = Btmtr()
        self.bot_redis = BotRedis()
        self.pika_producer = PikaProducer(
            ssm_get_parameters("rabbitmq_broker_id"),
            ssm_get_parameters("rabbitmq_user_username"),
            ssm_get_parameters("rabbitmq_user_password"),
            ssm_get_parameters("rabbitmq_broker_region"),
        )
        self.pika_producer.declare_queue(self.PIKA_QUEUE)

    def predict_bot_tweets(self, tweet):
        try:
            if self.bot_redis.account_exists(tweet):
                if self.bot_redis.account_isnot_bot(tweet):
                    # call rabbitmq
                    self.pika_producer.send_message(
                        exchange = "",
                        routing_key = self.PIKA_QUEUE,
                        body = tweet,
                    )
            else:
            # call botometer
                try:
                    is_tweet_bot = self.btmtr.botometer_regular(tweet)
                    self.bot_redis.set_account(tweet, is_tweet_bot)
                except RateLimitException:
                    # when ratelimit for the hour hits
                    # TODO: call rabbitmq
                    print("\nratelimit hits")
        except:
            # not sure if this is the right way to close the connection
            self.pika_producer.close()


