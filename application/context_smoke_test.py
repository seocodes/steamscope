import json
import logging

from context import build_deal_context
from db import list_games_by_snippet
from gemini_advisor import analyze_deal
from pymongo.errors import PyMongoError
from redis.exceptions import RedisError
from redis_client import build_advice_cache_key, create_redis_client

logger = logging.getLogger(__name__)


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


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


def read_search_term():
    return input("Enter part of the game title: ").strip()


def main():
    configure_logging()
    redis_client = create_redis_client()
    cache_status = "MISS"

    while True:
        print("""
            0 - Search game by title
            1 - Type a game title and proposed price to analyze a deal (case sensitive!!!)
            2 - Exit""")
        choice = input("Enter your choice: ").strip()

        if choice == "2":
            break

        elif choice == "0":
            try:
                snippet = read_search_term()
                games = list_games_by_snippet(snippet)
                print(f"Found {len(games)} games:")
                for game in games:
                    print(f"  - {game}")
            except ValueError as error:
                print(f"Error: {error}")
            except PyMongoError:
                logger.exception("MongoDB unavailable while searching for games")
                print("Could not access the game catalog. Please try again later.")
            except Exception:
                logger.exception("Unexpected error while searching for games")
                print("Could not search for games. Please try again.")
            continue

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
                    logger.warning(
                        "Redis unavailable, falling back to analysis without caching", exc_info=True
                    )
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
                print(error)
                continue
            except Exception:
                # Inclui automaticamente o traceback
                logger.exception("An unexpected error occurred while analyzing deal.")
                print("An unexpected error occurred, try again.")
                continue

        else:
            print("Invalid choice. Please enter 0, 1 or 2.")
            continue


if __name__ == "__main__":
    main()
