# import X = whole module | from X import Y = specific thing from the module
import re
import requests
import logging
import time
from datetime import datetime
from bs4 import BeautifulSoup

try:
    from application.db import insert_deals
except ModuleNotFoundError:
    from db import insert_deals

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validate_game_record(record):
    """
    Validate that a game record has proper data before MongoDB insert.
    
    Args:
        record (dict): Game data with title, url, prices, etc.
    
    Returns:
        tuple: (is_valid, error_message)
    
    Why validation?
    - Prevents corrupted data from poisoning ML training dataset
    - Catches parsing errors early (missing HTML elements, regex failures)
    - Makes MongoDB queries reliable (no unexpected None values)
    """
    
    # Check 1: Title exists and is reasonable length
    title = record.get("title", "")
    if not title or len(title) < 3 or len(title) > 200:
        return False, f"Invalid title: '{title}' (length must be 3-200)"
    
    # Check 2: URL is from Steam
    url = record.get("url", "")
    if "steampowered.com" not in url or len(url) < 10:
        return False, f"Invalid URL: '{url}' (must be steampowered.com link)"
    
    # Check 3: Prices are positive numbers
    original_price = record.get("original_price", 0)
    discounted_price = record.get("discounted_price", 0)
    
    # Handle None or non-numeric values
    try:
        original_price = float(original_price)
        discounted_price = float(discounted_price)
    except (TypeError, ValueError):
        return False, f"Prices not numeric: original={original_price}, discounted={discounted_price}"
    
    # Check 4: Discounted price should be <= original price (discount = price reduction)
    if discounted_price > original_price:
        return False, f"Discounted price ({discounted_price}) > original price ({original_price})"
    
    # Check 5: Discount % is between 0-100
    discount_pct = record.get("discount_pct", 0)
    if not isinstance(discount_pct, (int, float)) or discount_pct < 0 or discount_pct > 100:
        return False, f"Invalid discount %: {discount_pct} (must be 0-100)"
    
    # Check 6: scraped_at timestamp exists (for time-series data)
    scraped_at = record.get("scraped_at")
    if not scraped_at:
        return False, "Missing scraped_at timestamp"
    
    # All checks passed!
    return True, ""

def fetch_page(max_retries=3, timeout=10):
    """
    Fetch Steam specials page with safety features.
    
    Args:
        max_retries (int): How many times to retry on network failure
        timeout (int): How long to wait for server response (in seconds)
    
    Returns:
        BeautifulSoup object or None if all retries fail
    
    Why these features?
    - timeout: Prevents hanging forever if Steam is slow/unresponsive
    - max_retries: Network blips happen; one failure shouldn't kill the whole run
    - User-Agent: Steam blocks requests that look like bots; this looks like a real browser
    """
    url = "https://store.steampowered.com/search/?specials=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching Steam page (attempt {attempt + 1}/{max_retries})...")
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()  # Raise exception if status code is 4xx or 5xx
            
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
        
        # If we have retries left, wait before trying again
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            logger.info(f"Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
    
    logger.error(f"Failed to fetch page after {max_retries} attempts.")
    return None


def scrape_deals(page, rate_limit_delay=1):
    """
    Scrape all deals from page with deduplication.
    
    Args:
        page (BeautifulSoup): HTML page object
        rate_limit_delay (int): Seconds to sleep between processing (polite to Steam)
    
    Returns:
        list: List of valid game records (deduplicated by URL within this run)
    
    Why deduplication?
    - Same game sometimes appears twice on Steam search results (regional variants)
    - We only want one record per game per scrape run
    - URL is the unique identifier (same game = same URL)
    """
    deals = page.find_all("a", class_="search_result_row")
    logger.info(f"Found {len(deals)} game entries on page")
    
    seen_urls = set()  # Track URLs we've already processed in this run
    valid_records = []
    
    for i, deal in enumerate(deals):
        try:
            # Parse the game
            record = parse_game(deal)
            
            if record is None:
                continue  # Skip invalid records
            
            # Check for duplicates (same URL in this run)
            if record["url"] in seen_urls:
                logger.info(f"Skipping duplicate: {record['title']} (already seen in this run)")
                continue
            
            # Add to tracking set
            seen_urls.add(record["url"])
            valid_records.append(record)
            
            # Rate limiting: be polite to Steam's servers
            if rate_limit_delay > 0 and i < len(deals) - 1:
                time.sleep(rate_limit_delay)
        
        except Exception as e:
            logger.error(f"Unexpected error processing deal {i}: {e}")
            continue
    
    logger.info(f"✓ Scraped {len(valid_records)} valid unique games")
    return valid_records



def parse_game(element):
    """
    Extract game data from Steam HTML element with per-field error handling.
    
    Why try/except per field?
    - If title is missing, we skip that game entirely (invalid)
    - If rating is missing, we extract what we can and set rating to None (not critical for now)
    - Prevents one missing field from breaking the entire extraction
    
    Returns:
        dict or None: Game record if validation passes, None if invalid
    """
    record = {}
    
    # CRITICAL: Extract title (if this fails, skip entire game)
    try:
        title_span = element.find("span", class_="title")
        if not title_span:
            logger.warning("No title found for game element")
            return None
        record["title"] = title_span.text.strip()
    except Exception as e:
        logger.warning(f"Error extracting title: {e}")
        return None
    
    # CRITICAL: Extract URL (primary key for deduplication)
    try:
        url = element.get("href", "")
        if not url:
            logger.warning(f"No URL for game: {record['title']}")
            return None
        record["url"] = url
    except Exception as e:
        logger.warning(f"Error extracting URL: {e}")
        return None
    
    # Extract discount %
    try:
        discount_pct_div = element.find("div", class_="discount_pct")
        discount_pct_text = discount_pct_div.text.strip() if discount_pct_div else "0%"
        record["discount_pct"] = int(re.sub(r"[^\d]", "", discount_pct_text))
    except Exception as e:
        logger.warning(f"Error extracting discount % for {record['title']}: {e}")
        record["discount_pct"] = 0  # Default to no discount if parsing fails
    
    # Extract original price
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
    
    # Extract discounted price
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
    
    # Add scrape timestamp (for time-series tracking)
    record["scraped_at"] = datetime.now().isoformat()
    
    # VALIDATE before returning
    is_valid, error_msg = validate_game_record(record)
    if not is_valid:
        logger.warning(f"Invalid record for {record.get('title', 'Unknown')}: {error_msg}")
        return None
    
    logger.info(f"✓ Valid record: {record['title']} - {record['discount_pct']}% off")
    return record

if __name__ == "__main__":
    logger.info("Starting Steam scraper...")
    
    page = fetch_page(max_retries=3, timeout=10)
    
    if page is None:
        logger.error("Failed to fetch page. Exiting.")
        exit(1)
    
    valid_records = scrape_deals(page, rate_limit_delay=1)
    
    if not valid_records:
        logger.warning("No valid records scraped.")
        exit(0)
    
    inserted_count = insert_deals(valid_records)
    logger.info(f"Inserted {inserted_count} records into MongoDB")

    logger.info("=== Inserted Records ===")
    for record in valid_records:
        print(f"  {record['title']}: {record['discount_pct']}% off (${record['discounted_price']})")