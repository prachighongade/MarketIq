import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from data_fetcher import fetch_stock_data
from data_processor import process_data
from trend_analysis import analyze_trends

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run_pipeline():
    start = datetime.now()
    logger.info("Pipeline run started")
    try:
        raw = fetch_stock_data()
        processed = process_data(raw)
        analyze_trends(processed)
        duration = (datetime.now() - start).total_seconds()
        logger.info("Pipeline completed successfully in %.2fs", duration)
    except Exception:
        logger.exception("Pipeline run FAILED")


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_pipeline, CronTrigger(hour=16, minute=0))  # after NSE close
    scheduler.start()
    logger.info("Scheduler started")
    return scheduler