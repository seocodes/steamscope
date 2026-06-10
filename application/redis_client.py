import hashlib
import os

from dotenv import load_dotenv
from redis import Redis

load_dotenv()

def create_redis_client():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return Redis.from_url(redis_url, decode_responses=True)

def check_rate_limit(redis_client, key, limit, period):
    current_count = redis_client.incr(key)

    if current_count == 1:
        # Defines expiration time
        redis_client.expire(key, period)

    if current_count > limit:
        return False
    return True

def build_advice_cache_key(title, proposed_price):
    normalized_title = title.strip().lower()
    normalized_price = f"{proposed_price:.2f}".strip()
    raw_key = f"{normalized_title}:{normalized_price}"

    digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    return f"cache:advise:v1:{digest}"
