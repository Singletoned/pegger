# -*- coding: utf-8 -*-

class Some(object):
    def __init__(self, pattern):
        self.pattern = pattern

def match_some(text, pattern):
    match = []
    rest = list(text)
    while rest:
        char = rest[0]
        if pattern().pattern == char:
            match.append(rest.pop(0))
        else:
            break
    return ([pattern.__name__, "".join(match)], "".join(rest))

def match_text(text, pattern):
    """If the pattern matches the beginning of the text, parser it and
    return the rest"""
    if text.startswith(pattern()):
        rest = text[len(pattern()):]
        return ([pattern.__name__, pattern()], rest)
    else:
        return (None, None)

def match_tuple(text, pattern):
    "Match each of the patterns in the tuple in turn"
    result = []
    rest = text
    for sub_pattern in pattern():
        match, rest = do_parse(rest, sub_pattern)
        result.append(match)
    return (result, rest)
    

def do_parse(text, pattern):
    if text == pattern():
        return ([pattern.__name__, text], '')
    elif isinstance(pattern(), (str, unicode)):
        return match_text(text, pattern)
    elif isinstance(pattern(), tuple):
        return match_tuple(text, pattern)
    elif isinstance(pattern(), Some):
        return match_some(text, pattern)
    else:
        return (None, None)

def parse_string(text, pattern):
    match, rest = do_parse(text, pattern)
    return match
