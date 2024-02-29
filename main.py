import schedule
import time
import os

print('Scheduler initialised')
schedule.every(60).seconds.do(lambda: os.system(
    'scrapy crawl parking-availability'))
print('Next job is set to run at: ' + str(schedule.next_run()))

while True:
    schedule.run_pending()
    time.sleep(1)
