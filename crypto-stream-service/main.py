import time
import schedule

from lib.crypto_data import CryptoData

crypto_data = CryptoData()

cryptocurrencies = [
    "BTC",
    "ETH",
    "BNB",
    "XRP",
    "SOL",
    "ADA",
    "DOGE",
]

schedule.every().minute.at(":00").do(crypto_data.get_all_cryptocurrency_price, cryptocurrencies = cryptocurrencies)

while True:
    schedule.run_pending()
    time.sleep(1)