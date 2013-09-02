# -*- coding: utf-8 -*-

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
