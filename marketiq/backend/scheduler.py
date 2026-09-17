from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from data_fetcher import fetch_stock_data
from data_processor import process_data
from trend_analysis import analyze_trends

def run_pipeline():
    raw = fetch_stock_data()
    processed = process_data(raw)
    analyze_trends(processed)

scheduler = BackgroundScheduler()
scheduler.add_job(run_pipeline, CronTrigger(hour=16, minute=0))  # after NSE close
scheduler.start()

