from lib.btmtr import Btmtr
from lib.bot_redis import BotRedis

class TweetsPredictor:
    # not using botometer lite because accuracy disapointing

    BOTOMETER_REQUEST_LIMIT = 17000
    botometer_requests = 0

    def __init__(self):
        self.btmtr = Btmtr()
        self.bot_redis = BotRedis()

    def predict_bot_tweets(self, tweet):
        if self.bot_redis.account_exists(tweet):
            if self.bot_redis.account_isnot_bot(tweet):
                # TODO: call rabbitmq
                pass
        elif self.botometer_requests < self.BOTOMETER_REQUEST_LIMIT: 
        # call botometer
            is_tweet_bot = self.btmtr.botometer_regular(tweet)
            self.bot_redis.set_account(tweet, is_tweet_bot)
            self.botometer_requests += 1
        else:
            # TODO: skip bot validation and send to rabbitmq 
            pass



