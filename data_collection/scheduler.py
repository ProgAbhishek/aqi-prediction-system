from apscheduler.schedulers.blocking import BlockingScheduler
from fetch_data import fetch

scheduler = BlockingScheduler()

# Run every 1 hour
scheduler.add_job(fetch, 'interval', hours=1)
# scheduler.add_job(fetch, 'interval', minutes=1)

print("Scheduler started. Collecting AQI data every hour...")

# Run once immediately when the program starts
fetch()

try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    print("Scheduler stopped.")