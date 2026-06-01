import time
from django.core.cache import cache


def is_rate_limited(identifier, limit=60, period=60):
    current_window = int(time.time() // period)
    cache_key = f"rate_limit:{identifier}:{current_window}"

    count = cache.get(cache_key, 0)

    if count >= limit:
        return True

    cache.set(cache_key, count + 1, timeout=period)
    return False