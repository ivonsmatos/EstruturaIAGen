# Testes para o limitador de taxa
import time
from src.utils.rate_limiter import RateLimiter

def test_rate_limiter():
    limiter = RateLimiter(max_calls=2, period=1)
    assert limiter.is_allowed() is True
    assert limiter.is_allowed() is True
    assert limiter.is_allowed() is False
    time.sleep(1)
    assert limiter.is_allowed() is True