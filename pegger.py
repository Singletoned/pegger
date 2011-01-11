# -*- coding: utf-8 -*-

class Some(object):
    def __init__(self, pattern):
        self.pattern = pattern

def parse_string(text, pattern):
    if text == pattern():
        return [pattern.__name__, text]
    elif isinstance(pattern(), tuple):
        return [parse_string(sub_text, sub_pattern) for sub_text, sub_pattern in zip(text, pattern())]
    elif isinstance(pattern(), Some):
        return [pattern.__name__, text]
    else:
        return None
