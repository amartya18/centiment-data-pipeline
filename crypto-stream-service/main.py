import json
import time
import schedule

from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

def get_btc_price():
    result = cg.get_price(ids='bitcoin', vs_currencies='usd')
    print(json.dumps(result))

schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)