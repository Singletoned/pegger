# -*- coding: utf-8 -*-

import contextlib


def deep_bool(data):
    if isinstance(data, basestring):
        return bool(data)
    for item in data:
        try:
            if deep_bool(item):
                return True
        except TypeError:
            return bool(item)
    return False

def memoise(func):
    cache = dict()
    @contextlib.wraps(func)
    def _inner(*args, **kwargs):
        key = repr((args, kwargs))
        if cache.has_key(key):
            return cache[key]
        else:
            return cache.setdefault(key, func(*args, **kwargs))
    return _inner
