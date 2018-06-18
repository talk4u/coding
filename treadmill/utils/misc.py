import functools


__all__ = [
    'cached',
    'pretty_object_str',
    'ReprMixin'
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


def pretty_object_str(inst):
    type_name = type(inst).__name__
    if hasattr(inst, '__slots__') and inst.__slots__:
        props = {key: getattr(inst, key) for key in inst.__slots__}
    else:
        props = inst.__dict__
    props_str = ' '.join([
        f'{key}={value}'
        for key, value in props.items()
        if not key.startswith('_')
    ])
    return f'{type_name}({props_str})'


class ReprMixin(object):
    def __repr__(self):
        return pretty_object_str(self)
