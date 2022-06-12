from lib.stream_tweets import TwitterStreamTweets

if __name__ == "__main__":

    streamTweets = TwitterStreamTweets(
                debug_print = False,
                limit = 15
            )

    cryptocurrencies = [
                "BTC",
                "ETH",
                "BNB",
                "XRP",
                "SOL",
                "ADA",
                "DOGE",
            ]

    query = ""
    for coin in cryptocurrencies:
        if query:
            query += " OR \"${}\"".format(coin)
        else:
            query += "\"${}\"".format(coin)

    streamTweets.stream_tweets([
        "({} OR bitcoin OR ethereum OR XRP OR solana OR cardano OR dogecoin)".format(query),
        "-giveaway -give -free -trader -win -winner",
        "lang:en -is:retweet -is:reply -has:links",
        ])
