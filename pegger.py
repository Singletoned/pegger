# -*- coding: utf-8 -*-

def parse_string(text, pattern):
    if text == pattern():
        return [pattern.__name__, text]
    elif isinstance(pattern(), tuple):
        return [parse_string(sub_text, sub_pattern) for sub_text, sub_pattern in zip(text, pattern())]
    else:
        return None
