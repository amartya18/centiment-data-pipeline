import boto3

ssm = boto3.client("ssm", "ap-southeast-1")

def ssm_get_parameters(key):
    response = ssm.get_parameters(Names=[key], WithDecryption=True)

    for params in response["Parameters"]:
        return params["Value"]

def get_tweepy_filter(crypto):
    all_cryptos = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "BNB": "BNB",
        "XRP": "XRP",
        "SOL": "solana",
        "ADA": "cardano",
        "DOGE": "dogecoin",
    }
    general = " -giveaway -give -free -trader -win -winner lang:en -is:retweet -is:reply -has:links"

    filter = ""
    for key, value in all_cryptos.items():
        if crypto == key:
            filter = f"(\"${key}\" OR {value})" + filter
        # TODO: temporary disable, check if this filter needed 
        # else:
        #     filter += f" -\"${key}\" -{value}"
    filter += general

    return filter.strip()
