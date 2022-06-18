from dotenv import load_dotenv
import os

from rpy2 import robjects
from rpy2.robjects.vectors import StrVector
from rpy2.robjects import pandas2ri
import rpy2.robjects.packages as rpackages
import rpy2.robjects as ro

from rpy2.robjects.conversion import localconverter

load_dotenv()

utils = rpackages.importr("utils")

packnames = ("remotes")

names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
if len(names_to_install) > 0:
    utils.install_packages(StrVector(names_to_install))

if (not rpackages.isinstalled("tweetbotornot2")):
    remotes = robjects.r["install_github"]
    remotes("mkearney/tweetbotornot2")

tweetbotornot2 = rpackages.importr("tweetbotornot2")
rtweet = rpackages.importr("rtweet")

rtweet.create_token(
        app = os.environ.get("APP"),
        consumer_key = os.environ.get("CONSUMER_KEY"),
        consumer_secret = os.environ.get("CONSUMER_SECRET"),
        access_token = os.environ.get("ACCESS_TOKEN"),
        access_secret = os.environ.get("ACCESS_SECRET"),
        )


def predict_bot_username(twitter_username):
    twitter_username_vector = StrVector(twitter_username)

    prediction_r_df = tweetbotornot2.predict_bot(twitter_username_vector, token = rtweet.bearer_token())

    with localconverter(ro.default_converter + pandas2ri.converter):
        prediction_df = ro.conversion.rpy2py(prediction_r_df)


    result = {}
    for user in prediction_df.values:
        result[user[1]] = { "isBot": False, "prediction": user[2] }

    return result

