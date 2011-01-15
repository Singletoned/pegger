# -*- coding: utf-8 -*-

import string

class NoPatternFound(Exception):
    pass

class UnknownMatcherType(Exception):
    pass

class Matcher(object):
    """A base matcher"""
    def __init__(self, pattern):
        self.pattern = pattern


class Some(Matcher):
    """A matcher that matches any one char repeatedly"""
    pass


class Ignore(Matcher):
    """A matcher that matches any one char repeatedly"""
    pass


class OneOf(Matcher):
    """A matcher that matches the first matching matcher"""
    def __init__(self, *options):
        self.options = options


class Words(object):
    """A matcher that matches any sequence of letters and spaces"""
    letters = string.uppercase + string.lowercase + " "
    
    def __init__(self, letters=None):
        if letters:
            self.letters = letters
        

def match_some(text, pattern, name):
    """Match the given char repeatedly"""
    match = []
    rest = list(text)
    while rest:
        char = rest[0]
        if pattern.pattern == char:
            match.append(rest.pop(0))
        else:
            break
    if not match:
        raise NoPatternFound
    return ([name, "".join(match)], "".join(rest))

def match_words(text, pattern, name):
    "Match everything that is part of pattern.letters"
    match = []
    rest = list(text)
    letters = pattern.letters
    while rest:
        char = rest[0]
        if char in letters:
            match.append(rest.pop(0))
        else:
            break
    if not match:
        raise NoPatternFound
    return ([name, "".join(match)], "".join(rest))

def match_text(text, pattern, name):
    """If the pattern matches the beginning of the text, parser it and
    return the rest"""
    if text.startswith(pattern):
        rest = text[len(pattern):]
        return ([name, pattern], rest)
    else:
        raise NoPatternFound

def match_tuple(text, pattern, name):
    "Match each of the patterns in the tuple in turn"
    result = []
    rest = text
    for sub_pattern in pattern:
        match, rest = do_parse(rest, sub_pattern)
        if match:
            if (not match[0]) or (match[0] == "<lambda>"):
                match = match[1]
            result.append(match)
    if len(result) == 1:
        result = result[0]
    result = [name, result]
    return (result, rest)

def match_ignore(text, pattern, name):
    "Match the pattern, but return no result"
    if text.startswith(pattern.pattern):
        rest = text[len(pattern.pattern):]
        return ([], rest)
    else:
        raise NoPatternFound

def match_one_of(text, pattern, name):
    """Match one of the patterns given"""
    for sub_pattern in pattern.options:
        try:
            match, rest = do_parse(text, sub_pattern)
        except NoPatternFound:
            continue
        if match:
            if (not match) or (match[0] == "<lambda>"):
                match = match[1]
            return (match, rest)


matchers = {
    str: match_text,
    unicode: match_text,
    tuple: match_tuple,
    Some: match_some,
    Words: match_words,
    Ignore: match_ignore,
    OneOf: match_one_of,
    }

def do_parse(text, pattern):
    """Dispatch to the correct function based on the type of the pattern"""
    pattern, pattern_name, pattern_type = get_pattern_info(pattern)
    try:
        matcher_func = matchers[pattern_type]
        result = matcher_func(text, pattern, pattern_name)
        return result
    except KeyError:
        raise UnknownMatcherType

def parse_string(text, pattern):
    match, rest = do_parse(text, pattern)
    return match

def get_pattern_info(pattern):
    pattern_name = ""
    if callable(pattern):
        pattern_name = pattern.__name__
        pattern = pattern()
        if pattern_name == "<lambda>":
            pattern_name = ""
    pattern_type = type(pattern)
    return pattern, pattern_name, pattern_type
    
