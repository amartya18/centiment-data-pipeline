import schedule
import time

def job():
    print("1 minute func triggered")

def job_with_argument(name):
    print(f"30 seconds func triggered: {name}")

schedule.every(1).minutes.do(job)

schedule.every(30).seconds.do(job_with_argument, name="test")

while True:
    schedule.run_pending()
    time.sleep(1)