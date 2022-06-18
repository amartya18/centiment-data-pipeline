import botometer
from dotenv import load_dotenv
import os

load_dotenv()

class Btmtr:
    BOTOMETER_LITE_THRESHOLD = 0.75
    BOTOMETER_REGULAR_THRESHOLD = 0.90

    def __init__(self) -> None:
        rapidapi_key = os.environ.get("RAPIDAPI_KEY")

        twitter_app_auth = {
                "consumer_key": os.environ.get("CONSUMER_KEY"),
                "consumer_secret": os.environ.get("CONSUMER_SECRET"),
                "access_token": os.environ.get("ACCESS_TOKEN"),
                "access_token_secret": os.environ.get("ACCESS_SECRET"),
                }

        self.bom_regular = botometer.Botometer(wait_on_ratelimit=True, rapidapi_key=rapidapi_key, **twitter_app_auth)
        self.bom_lite = botometer.BotometerLite(rapidapi_key=rapidapi_key, **twitter_app_auth)

    def botometer_lite(self, tweets_list):
        user_ids_list = []
        for tweet in tweets_list:
            user_id = tweet["includes"]["users"][0]["id"]
            user_ids_list.append(user_id)

        response = self.bom_lite.check_accounts_from_user_ids(user_ids_list)

        print("PREDICTION:\n")
        print(response)
        print("\n")

    def botometer_regular(self, tweet):
        user_id = tweet["includes"]["users"][0]["id"]
        response = self.bom_regular.check_account(user_id)

        print("PREDICTION:\n")
        print(response)
        print("\n")

