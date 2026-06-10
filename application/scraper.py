import logging
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

try:
    from application.db import insert_deals
except ModuleNotFoundError:
    from db import insert_deals

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validate_game_record(record):
    title = record.get("title", "")
    if not title or len(title) < 3 or len(title) > 200:
        return False, f"Invalid title: '{title}' (length must be 3-200)"
    
    url = record.get("url", "")
    if "steampowered.com" not in url or len(url) < 10:
        return False, f"Invalid URL: '{url}' (must be steampowered.com link)"
    
    original_price = record.get("original_price", 0)
    discounted_price = record.get("discounted_price", 0)
    
    try:
        original_price = float(original_price)
        discounted_price = float(discounted_price)
    except (TypeError, ValueError):
        return False, f"Prices not numeric: original={original_price}, discounted={discounted_price}"
    
    if discounted_price > original_price:
        return False, f"Discounted price ({discounted_price}) > original price ({original_price})"
    
    discount_pct = record.get("discount_pct", 0)
    if not isinstance(discount_pct, (int, float)) or discount_pct < 0 or discount_pct > 100:
        return False, f"Invalid discount %: {discount_pct} (must be 0-100)"
    
    scraped_at = record.get("scraped_at")
    if not scraped_at:
        return False, "Missing scraped_at timestamp"
    
    return True, ""

def fetch_page(page, max_retries=3, timeout=10):
    base_url = "https://store.steampowered.com/search/?specials=1"
    url = f"{base_url}&page={page}" if page > 1 else base_url
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching Steam page {page} (attempt {attempt + 1}/{max_retries})...")
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            page = BeautifulSoup(response.content, "html.parser")
            logger.info(f"Page title: {page.title.text}")
            logger.info(f"Status code: {response.status_code}")
            
            return page
        
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt + 1}. Server took longer than {timeout}s to respond.")
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error on attempt {attempt + 1}. Network issue or server down.")
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error on attempt {attempt + 1}: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error on attempt {attempt + 1}: {e}")
        
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            logger.info(f"Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
    
    logger.error(f"Failed to fetch page after {max_retries} attempts.")
    return None


def scrape_deals(page, rate_limit_delay=1, seen_urls=None):
    deals = page.find_all("a", class_="search_result_row")
    logger.info(f"Found {len(deals)} game entries on page")

    if seen_urls is None:
        seen_urls = set()
        
    valid_records = []
    
    for i, deal in enumerate(deals):
        try:
            record = parse_game(deal)
            
            if record is None:
                continue
            
            if record["url"] in seen_urls:
                logger.info(f"Skipping duplicate: {record['title']} (already seen in this run)")
                continue
            
            seen_urls.add(record["url"])
            valid_records.append(record)
            
            if rate_limit_delay > 0 and i < len(deals) - 1:
                time.sleep(rate_limit_delay)
        
        except Exception as e:
            logger.error(f"Unexpected error processing deal {i}: {e}")
            continue
    
    logger.info(f"✓ Scraped {len(valid_records)} valid unique games")
    return valid_records



def parse_game(element):
    record = {}
    
    try:
        title_span = element.find("span", class_="title")
        if not title_span:
            logger.warning("No title found for game element")
            return None
        record["title"] = title_span.text.strip()
    except Exception as e:
        logger.warning(f"Error extracting title: {e}")
        return None
    
    try:
        url = element.get("href", "")
        if not url:
            logger.warning(f"No URL for game: {record['title']}")
            return None
        record["url"] = url
    except Exception as e:
        logger.warning(f"Error extracting URL: {e}")
        return None
    
    try:
        discount_pct_div = element.find("div", class_="discount_pct")
        discount_pct_text = discount_pct_div.text.strip() if discount_pct_div else "0%"
        record["discount_pct"] = int(re.sub(r"[^\d]", "", discount_pct_text))
    except Exception as e:
        logger.warning(f"Error extracting discount % for {record['title']}: {e}")
        record["discount_pct"] = 0
    
    try:
        original_price_div = element.find("div", class_="discount_original_price")
        if original_price_div:
            price_text = original_price_div.text.strip()
            matches = re.findall(r"\d+[.,]\d+", price_text)
            record["original_price"] = float(matches[0].replace(",", ".")) if matches else 0.0
        else:
            record["original_price"] = 0.0
    except Exception as e:
        logger.warning(f"Error extracting original price for {record['title']}: {e}")
        record["original_price"] = 0.0
    
    try:
        final_price_div = element.find("div", class_="discount_final_price")
        if final_price_div:
            price_text = final_price_div.text.strip()
            matches = re.findall(r"\d+[.,]\d+", price_text)
            record["discounted_price"] = float(matches[0].replace(",", ".")) if matches else 0.0
        else:
            record["discounted_price"] = 0.0
    except Exception as e:
        logger.warning(f"Error extracting discounted price for {record['title']}: {e}")
        record["discounted_price"] = 0.0
    
    record["scraped_at"] = datetime.now().isoformat()
    
    is_valid, error_msg = validate_game_record(record)
    if not is_valid:
        logger.warning(f"Invalid record for {record.get('title', 'Unknown')}: {error_msg}")
        return None
    
    logger.info(f"✓ Valid record: {record['title']} - {record['discount_pct']}% off")
    return record

if __name__ == "__main__":
    logger.info("Starting Steam scraper...")
    total_pages = 25
    all_records = []
    seen_urls = set()

    for page in range(10, total_pages + 1):
        scrapped_page = fetch_page(page, max_retries=3, timeout=10)
        if scrapped_page is None:
            logger.warning(f"Failed to fetch page {page}. Skipping.")
            continue
    
        valid_records = scrape_deals(scrapped_page, rate_limit_delay=1, seen_urls=seen_urls)
        all_records.extend(valid_records)
        time.sleep(1)
        
        if not valid_records:
            logger.warning(f"No valid records scraped from page {page}.")
            continue
    
    if not all_records:
        logger.warning("No valid records scraped.")
        exit(0)
    
    inserted_count = insert_deals(all_records)
    logger.info(f"Inserted {inserted_count} records into MongoDB")

    logger.info("=== Inserted Records ===")
    for record in all_records:
        print(f"  {record['title']}: {record['discount_pct']}% off (${record['discounted_price']})")
