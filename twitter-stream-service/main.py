from lib.stream_tweets import TwitterStreamTweets, ssm_get_parameters

if __name__ == "__main__":
    ip_detect_bot_service = ssm_get_parameters("ip_detect_bot_service")

    streamTweets = TwitterStreamTweets(
                rpc_url = f"http://{ip_detect_bot_service}:5001",
                debug_print = False,
                limit = None,
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

    streamTweets.stream_tweets(cryptocurrencies)
