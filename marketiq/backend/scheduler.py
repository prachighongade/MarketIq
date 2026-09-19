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

import logging
from datetime import datetime

logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def run_daily_pipeline():
    start = datetime.now()
    logging.info("Pipeline run started")
    try:
        symbols = ["TCS", "RELIANCE", "INFY", "HDFCBANK", "ICICIBANK"]
        for symbol in symbols:
            fetch_data(symbol)
            process_data(symbol)
            analyze_trend(symbol)
        duration = (datetime.now() - start).total_seconds()
        logging.info(f"Pipeline run completed successfully — {len(symbols)} symbols in {duration:.2f}s")
    except Exception as e:
        logging.error(f"Pipeline run FAILED: {e}", exc_info=True)

