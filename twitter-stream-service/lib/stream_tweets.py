# import xmlrpc.client
from dotenv import load_dotenv
import tweepy
import json
import os

# rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:8000")

load_dotenv()

class TwitterAuth():
    ''' Twitter Authentication'''
    consumer_key = os.environ['api_key']
    consumer_secret = os.environ['api_key_secret']
    access_token = os.environ['access_token']
    access_token_secret = os.environ['access_token_secret']
    bearer_token = os.environ['bearer_token']

class ListenerStreamTweets(tweepy.StreamingClient):
    limit = None
    amount_of_tweets = 0
    debug_print = False
    viable_sources = ['Twitter for iPhone', 'Twitter for Android', 'Twitter Web App']

    def __init__(self, bearer_token, debug_print, limit):
        super().__init__(bearer_token)
        self.debug_print = debug_print
        self.limit = limit

    def on_data(self, raw_data):
        data = json.loads(raw_data)

        if self.debug_print:
            self.print_data(data)
        else: # call detect bot rpc
            if (self.__filter_source__(data)):
                # rpc.process_tweet(data)
                self.print_data(data)

        if self.limit: # limit amount of tweets streamed
            self.amount_of_tweets += 1
            if self.amount_of_tweets == self.limit:
                self.disconnect()

    def __filter_source__(self, data):
        tweet_source = data['data']['source']
        return True if tweet_source in self.viable_sources else False

    def print_data(self, data):
        print('\n===============================================\n')
        print("tweet {} :\n".format(self.amount_of_tweets))
        print('{}:\n{}\n'.format(data['includes']['users'][0]['username'], data['data']['text']))
        
    def on_closed(self):
        print("\nTwitter Stream connection closed! :(\n")

    def on_connect(self):
        print("\nTwitter Stream connection established! :)\n")

class TwitterStreamTweets():
    def __init__(self, debug_print, limit = 5):
        self.twitterAuth = TwitterAuth()
        self.debug_print = debug_print
        self.limit = limit

    def __delete_stream_rules__(self, stream_tweets):
        tweepy_streamrules = stream_tweets.get_rules().data

        if tweepy_streamrules:
            for rule in tweepy_streamrules:
                stream_tweets.delete_rules(rule.id)


    def stream_tweets(self, keywords):
        stream_tweets = ListenerStreamTweets(
            self.twitterAuth.bearer_token,
            self.debug_print,
            self.limit,
        )

        keywords_string = ' '.join(keywords)

        self.__delete_stream_rules__(stream_tweets)

        stream_tweets.add_rules(
            [
                tweepy.StreamRule(value = keywords_string, tag = 'cryptocurrency tweets'),
            ]
        )

        print("Twitter rule used: ", stream_tweets.get_rules())

        stream_tweets.filter(expansions="author_id", tweet_fields=["source", "created_at"])
