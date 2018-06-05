import functools


__all__ = [
    'cached'
]


def cached(fn):
    cache_key = f'_cache_{fn.__name__}'

    @functools.wraps(fn)
    def decorator(self, *args, **kwargs):
        if hasattr(self, cache_key):
            return getattr(self, cache_key)
        return_value = fn(self, *args, **kwargs)
        setattr(self, cache_key, return_value)
        return return_value

    return decorator
