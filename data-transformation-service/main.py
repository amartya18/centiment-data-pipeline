from lib.pika_consumer import PikaConsumer
from lib.tweet_sentiment import TweetSentiment
from lib.helper import ssm_get_parameters

if __name__ == "__main__":
    tweet_sentiment = TweetSentiment()

    basic_message_receiver = PikaConsumer(
        ssm_get_parameters("rabbitmq_broker_id"),
        ssm_get_parameters("rabbitmq_user_username"),
        ssm_get_parameters("rabbitmq_user_password"),
        ssm_get_parameters("rabbitmq_broker_region"),
        exchange = "",
        queue = "twitter_stream_ttl",
        args = { "x-message-ttl": 9000 },
    )

    # temporarily test
    # try:
    basic_message_receiver.consume_messages("", "twitter_stream_ttl", tweet_sentiment.process_data)

    basic_message_receiver.close()

    # except:
    #     basic_message_receiver.close()