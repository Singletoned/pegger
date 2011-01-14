# -*- coding: utf-8 -*-

import string

class NoPatternFound(Exception):
    pass


class Some(object):
    """A matcher that matches any one char repeatedly"""
    def __init__(self, pattern):
        self.pattern = pattern


class Ignore(object):
    """A matcher that matches any one char repeatedly"""
    def __init__(self, pattern):
        self.pattern = pattern


class Words(object):
    """A matcher that matches any sequence of letters and spaces"""
    letters = string.uppercase + string.lowercase + " "
    
    def __init__(self, letters=None):
        if letters:
            self.letters = letters
        

def match_some(text, pattern):
    """Match the given char repeatedly"""
    match = []
    rest = list(text)
    while rest:
        char = rest[0]
        if pattern().pattern == char:
            match.append(rest.pop(0))
        else:
            break
    if not match:
        raise NoPatternFound
    return ([pattern.__name__, "".join(match)], "".join(rest))

def match_words(text, pattern):
    "Match everything that is part of pattern.letters"
    match = []
    rest = list(text)
    letters = pattern().letters
    while rest:
        char = rest[0]
        if char in letters:
            match.append(rest.pop(0))
        else:
            break
    if not match:
        raise NoPatternFound
    return ([pattern.__name__, "".join(match)], "".join(rest))

def match_text(text, pattern):
    """If the pattern matches the beginning of the text, parser it and
    return the rest"""
    if text.startswith(pattern()):
        rest = text[len(pattern()):]
        return ([pattern.__name__, pattern()], rest)
    else:
        raise NoPatternFound

def match_tuple(text, pattern):
    "Match each of the patterns in the tuple in turn"
    result = []
    rest = text
    for sub_pattern in pattern():
        match, rest = do_parse(rest, sub_pattern)
        if match:
            if match[0] == "<lambda>":
                match = match[1]
            result.append(match)
    if len(result) == 1:
        result = result[0]
    result = [pattern.__name__, result]
    return (result, rest)

def match_ignore(text, pattern):
    "Match the pattern, but return no result"
    if text.startswith(pattern().pattern):
        rest = text[len(pattern().pattern):]
        return ([], rest)
    else:
        raise NoPatternFound
    

matchers = {
    str: match_text,
    unicode: match_text,
    tuple: match_tuple,
    Some: match_some,
    Words: match_words,
    Ignore: match_ignore,
    }

def do_parse(text, pattern):
    """Dispatch to the correct function based on the type of the pattern"""
    if text == pattern():
        return ([pattern.__name__, text], '')
    pattern_type = type(pattern())
    try:
        matcher_func = matchers[pattern_type]
        result = matcher_func(text, pattern)
        return result
    except KeyError:
        return (None, None)

def parse_string(text, pattern):
    match, rest = do_parse(text, pattern)
    return match
