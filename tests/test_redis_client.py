from application.redis_client import build_advice_cache_key, check_rate_limit

# Redis client Mock
class FakeRedisClient:
    def __init__(self):
        self.values = {}
        self.expirations = {}
        self.expirations_calls = 0

    def incr(self, key):
        self.values[key] = self.values.get(key, 0) + 1
        return self.values[key]

    def expire(self, key, period):
        self.expirations[key] = period
        self.expirations_calls += 1

def test_build_advice_cache_key():
    key_a = build_advice_cache_key("Elden Ring", 79.99)
    key_b = build_advice_cache_key(" elDen ring  ", 79.99)
    assert key_a == key_b

def test_build_advice_cache_key_price_normalization():
    key_a = build_advice_cache_key("Elden Ring", 79.99)
    key_b = build_advice_cache_key("Elden Ring", 79.990001)
    assert key_a == key_b

def test_check_rate_limit():
    # Arrange
    redis_client = FakeRedisClient()
    key = "rate_limit:advise:127.0.0.1"
    
    # Act
    check_rate_limit(redis_client, key, limit=3, period=45)
    check_rate_limit(redis_client, key, limit=3, period=45)
    check_rate_limit(redis_client, key, limit=3, period=45)
    
    # Assert
    assert check_rate_limit(redis_client, key, limit=3, period=45) is False

def test_check_rate_limit_sets_expiration_only_once():
    # Arrange
    redis_client = FakeRedisClient()
    key = "rate_limit:advise:127.0.0.1"

    # Act
    check_rate_limit(redis_client, key, limit=3, period=45)
    check_rate_limit(redis_client, key, limit=3, period=45)
    check_rate_limit(redis_client, key, limit=3, period=45)

    # Assert
    assert redis_client.expirations[key] == 45
    assert redis_client.expirations_calls == 1
    
