from ratelimit import RateLimitException

from lib.btmtr import Btmtr
from lib.bot_redis import BotRedis

class TweetsPredictor:
    # not using botometer lite because accuracy disapointing

    def __init__(self):
        self.btmtr = Btmtr()
        self.bot_redis = BotRedis()

    def predict_bot_tweets(self, tweet):
        if self.bot_redis.account_exists(tweet):
            print("account exists in reddis")
            if self.bot_redis.account_isnot_bot(tweet):
                print("account is not bot")
                # TODO: call rabbitmq
        else:
        # call botometer
            try:
                is_tweet_bot = self.btmtr.botometer_regular(tweet)
                self.bot_redis.set_account(tweet, is_tweet_bot)
            except RateLimitException:
                # when ratelimit for the hour hits
                # call rabbitmq
                print("\nratelimit hits")


