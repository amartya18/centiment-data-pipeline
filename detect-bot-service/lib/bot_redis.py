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

    def get_account(self, tweet):
        user_id = self.__get_tweet_user_id__(tweet)

        # if account exists in redis already
        account_exist = bool(self.rds.exists(user_id)) 
        return True if account_exist else False
    
    def set_account(self, tweet, value):
        user_id = self.__get_tweet_user_id__(tweet)
        print("redis user stored:", user_id, int(value))
        self.rds.set(user_id, int(value))

    def exists_account(self, tweet):
        user_id = self.__get_tweet_user_id__(tweet)
        return self.rds.exists(user_id)
