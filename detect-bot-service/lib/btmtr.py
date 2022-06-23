import botometer
import os

from lib.helper import ssm_get_parameters

class Btmtr:
    # overall display score threshold
    BOTOMETER_REGULAR_THRESHOLD = 2

    def __init__(self):
        rapidapi_key = ssm_get_parameters("btmtr_rapidapi_key")

        twitter_app_auth = {
            "consumer_key": ssm_get_parameters('twitter_api_key'),
            "consumer_secret": ssm_get_parameters('twitter_api_key_secret'),
            "access_token": ssm_get_parameters('twitter_access_token'),
            "access_token_secret": ssm_get_parameters('twitter_access_token_secret'),
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

        overall_display_score = response["display_scores"]["english"]["overall"]
        is_bot = True if overall_display_score > self.BOTOMETER_REGULAR_THRESHOLD else False

        # bot binary classification based on: https://botometer.osome.iu.edu/faq
        return is_bot

