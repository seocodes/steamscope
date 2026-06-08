import os

from dotenv import load_dotenv
from redis import Redis

load_dotenv()

def create_redis_client():
    redis_url = os.getenv("REDIS_URL")
    return Redis.from_url(redis_url, decode_responses=True)

def check_rate_limit(redis_client, key, limit, period):
    current_count = redis_client.incr(key)

    if current_count == 1:
        # Define expiration time (I'll probably put a 45s time period)
        redis_client.expire(key, period)

    if current_count > limit:
        return False
    return True