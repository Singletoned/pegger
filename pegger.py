# -*- coding: utf-8 -*-

def parse_string(text, pattern):
    if text == pattern():
        return [pattern.__name__, text]
    else:
        return None
