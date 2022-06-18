from btmtr import Btmtr

class TweetsPredictor:
    BOTOMETER_LITE_TWEETS_LIMIT = 3
    BOTOMETER_LITE_REQUEST_LIMIT = 170
    BOTOMETER_REGULAR_REQUEST_LIMIT = 15000

    twitter_tweets_batch = []
    botometer_lite_requests = 0
    botometer_regular_requests = 0

    def __init__(self):
        self.btmtr = Btmtr()


    def predict_bot_tweets(self, tweet):
        if self.botometer_lite_requests < self.BOTOMETER_LITE_REQUEST_LIMIT:
            if len(self.twitter_tweets_batch) >= self.BOTOMETER_LITE_TWEETS_LIMIT:
                # botometerlite bulk
                self.btmtr.botometer_lite(self.twitter_tweets_batch)
                print("A")

                self.twitter_tweets_batch.clear()

            self.twitter_tweets_batch.append(tweet)
            self.botometer_lite_requests += 1
            print("B")

        elif self.botometer_regular_requests < self.BOTOMETER_REGULAR_REQUEST_LIMIT:
            self.btmtr.botometer_regular(tweet)
            self.botometer_regular_requests += 1
            print("C")


