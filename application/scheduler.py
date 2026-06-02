import logging
import os
import time
from pathlib import Path

import schedule

try:
    from application.db import insert_deals
    from application.scraper import fetch_page, scrape_deals
except ModuleNotFoundError:
    from db import insert_deals
    from scraper import fetch_page, scrape_deals

DEFAULT_SCRAPE_TIME = "06:00"

def configure_logging():
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("steamscope.scheduler")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler = logging.FileHandler(logs_dir / "scraper.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def validate_time_str(time_str):
    try:
        hours, minutes = time_str.split(":")
        h = int(hours)
        m = int(minutes)
        if 0 <= h <= 23 and 0 <= m <= 59:
            return time_str
    except (ValueError, AttributeError):
        pass

    raise ValueError(f"Invalid SCRAPE_TIME '{time_str}'. Use 24h format HH:MM (example: 14:30).")


def run_scraper_job(logger):
    logger.info("Starting scheduled scraper run...")

    total_pages = 3
    all_records = []
    seen_urls = set()  

    for page in range(1, total_pages + 1):
        page = fetch_page(page, max_retries=3, timeout=10)
        if page is None:
            logger.warning(f"Failed to fetch page {page}. Skipping.")
            continue
    
        valid_records = scrape_deals(page, rate_limit_delay=1, seen_urls=seen_urls)
        all_records.extend(valid_records)
        time.sleep(1)
        
        if not valid_records:
            logger.warning(f"No valid records scraped from page {page}.")
            continue
    
    if not all_records:
        logger.warning("No valid records scraped.")
        exit(0)
    
    inserted_count = insert_deals(all_records)
    logger.info("Scraper run completed. Inserted %s records.", inserted_count)


def start_scheduler():
    logger = configure_logging()

    scrape_time = validate_time_str(os.getenv("SCRAPE_TIME", DEFAULT_SCRAPE_TIME))
    run_on_startup = os.getenv("RUN_ON_STARTUP", "false").strip().lower() == "true"

    schedule.every().day.at(scrape_time).do(run_scraper_job, logger=logger)
    logger.info("Scheduler started. Job set to run daily at %s.", scrape_time)

    if run_on_startup:
        logger.info("RUN_ON_STARTUP=true detected. Executing scraper immediately once.")
        run_scraper_job(logger)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user.")
