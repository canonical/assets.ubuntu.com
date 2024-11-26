import time
from functools import lru_cache as _lru_cache


def lru_cache(*, ttl_seconds, maxsize=128):
    def deco(foo):
        @_lru_cache(maxsize=maxsize)
        def cached_with_ttl(*args, ttl_hash, **kwargs):
            return foo(*args, **kwargs)

        def inner(*args, **kwargs):
            return cached_with_ttl(
                *args, ttl_hash=round(time.time() / ttl_seconds), **kwargs
            )

        return inner

    return deco
