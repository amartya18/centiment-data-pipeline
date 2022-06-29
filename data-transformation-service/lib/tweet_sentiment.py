import pickle

from lib.influxdb_connector import InfluxdbConnector
from lib.tweet_preprocessor import TweetPreprocess
from lib.vader_sentiment import VaderSentiment

class TweetSentiment:
    def __init__(self):
        self.tweet_preprocess = TweetPreprocess()
        self.vader_sentiment = VaderSentiment()
        self.influxdb_connector = InfluxdbConnector()

    def convert_polarity_percentage(self, polarity):
        compound = polarity["compound"]
        percentage = (compound + 1) / 2 * 100
        return round(percentage, 1)

    def process_data(self, ch, method, properties, body):
        data = pickle.loads(body)

        # disable preprocessing because it reduces vader accuracy
        # source: https://towardsdatascience.com/are-you-scared-vader-understanding-how-nlp-pre-processing-impacts-vader-scoring-4f4edadbc91d
        # cleaned_text = self.tweet_preprocess.process_data(data["data"]["text"])
        # data["data"]["cleaned_text"] = cleaned_text

        polarity = self.vader_sentiment.get_polarity(data["data"]["text"])
        percentage = self.convert_polarity_percentage(polarity)

        data["data"]["sentiment"] = percentage

        # print("--------------")
        # print("{}\n\npercentage: {}% polarity: {}".format(data["data"]["text"], percentage, polarity))
        # print("--------------\n")

        self.influxdb_connector.insert_tweet(data)

