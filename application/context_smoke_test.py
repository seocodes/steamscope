import json
import logging

from context import build_deal_context
from gemini_advisor import analyze_deal
from redis.exceptions import RedisError
from redis_client import build_advice_cache_key, create_redis_client


def build_context(title, proposed_price):
    context = build_deal_context(title, proposed_price)
    return context


def read_proposed_price():
    raw_price = input("Enter a proposed price: ").strip().replace(",", ".")
    try:
        proposed_price = float(raw_price)
    except ValueError as exc:
        raise ValueError("Invalid price. Please enter a valid number.") from exc

    if proposed_price < 0:
        raise ValueError("Price cannot be negative.")
        
    return proposed_price

def read_title():
    title = input("Enter the game title: ").strip()

    if not title:
        raise ValueError("Title cannot be empty.")
    
    return title

def main():
    redis_client = create_redis_client()
    cache_status = "MISS"
    logger = logging.getLogger(__name__)
    while True:
        print("""
            1 - Type a game title and proposed price to analyze a deal
            2 - Exit""")
        choice = input("Enter your choice: ").strip()
        
        if choice == "2":
            break
    
        elif choice == "1":
            try:
                title = read_title()
                proposed_price = read_proposed_price()

                try:
                    cache_key = build_advice_cache_key(title, proposed_price)
                    cached = redis_client.get(cache_key)

                    if cached:
                        advice = json.loads(cached)
                        cache_status = "HIT"
                    else:
                        ctx = build_context(title, proposed_price)
                        advice = analyze_deal(ctx)
                        cache_status = "MISS"

                        redis_client.setex(
                                cache_key,
                                300,  # 5 minutes by default
                                json.dumps(advice),
                            )
                        
                except RedisError:
                    logger.warning("Redis unavailable, falling back to analysis without caching")
                    cache_status = "BYPASS"

                    # Fallback
                    ctx = build_context(title, proposed_price)
                    advice = analyze_deal(ctx)

                print("-----------------------------------------")
                for key, value in advice.items():
                    if key == "key_insights":
                        print("KEY INSIGHTS:")
                        for insight in value:
                            print(f"  - {insight}")
                    else:
                        print(f"{key}: {value}")
                print("-----------------------------------------")

                print(f"Cache status for this query: {cache_status}")
            
            except ValueError as error: 
                print(f"{error}")
                continue
            except Exception as error:
                print(f"An unexpected error occurred: {error}")
                continue

    
        else:
            print("Invalid choice. Please enter 1 or 2.")
            continue

if __name__ == "__main__":
    main()
