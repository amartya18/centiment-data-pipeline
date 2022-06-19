from imp import is_builtin
from redis.cluster import RedisCluster
from lib.helper import ssm_get_parameters

class BotRedis:
    def __init__(self):
        self.rds = RedisCluster(
            host = ssm_get_parameters("redis_cluster_host"),
            port = 6379, 
            username = ssm_get_parameters("redis_user_username"), 
            password = ssm_get_parameters("redis_user_password"),
            ssl = True
        )

    def ping(self):
        return self.rds.ping()

    def __get_tweet_user_id__(self, tweet):
        return tweet["includes"]["users"][0]["id"]

    def account_exists(self, tweet):
        user_id = self.__get_tweet_user_id__(tweet)

        # if account exists in redis already
        return bool(self.rds.exists(user_id)) 
    
    def set_account(self, tweet, value):
        # value true == account is bot
        user_id = self.__get_tweet_user_id__(tweet)
        self.rds.set(user_id, int(value))

    def account_isnot_bot(self, tweet):
        user_id = self.__get_tweet_user_id__(tweet)
        is_bot = bool(int(self.rds.get(user_id)))
        return not is_bot
