# -*- coding: utf-8 -*-

import string
import cgi

import utils


class NoPatternFound(Exception):
    pass

class UnknownMatcherType(Exception):
    pass

class Matcher(object):
    """A base matcher"""


class PatternMatcher(Matcher):
    """A base Matcher that has a pattern"""
    def __init__(self, pattern):
        self.pattern = pattern

    def __repr__(self):
        return "<%s pattern=%r>" % (self.__class__.__name__, self.pattern)


class OptionsMatcher(Matcher):
    """A base Matcher with a list of options"""
    def __init__(self, *options):
        self.options = options

    def __repr__(self):
        return "<%s options=%r>" % (self.__class__.__name__, self.options)


class CountOf(Matcher):
    """A matcher that matches count items"""
    def __init__(self, count, pattern):
        self.count = count
        self.pattern = pattern


class Insert(Matcher):
    """A matcher that inserts some text into the result"""
    def __init__(self, text):
        self.text = text

class Some(PatternMatcher):
    """A matcher that matches any one char repeatedly"""


class Ignore(PatternMatcher):
    """A matcher that matches any one char repeatedly"""


class Not(PatternMatcher):
    """A matcher that matches any string that isn't the pattern"""

class Join(PatternMatcher):
    "A matcher that joins together any consecutive strings"

class OneOf(OptionsMatcher):
    """A matcher that matches the first matching matcher"""


class AllOf(OptionsMatcher):
    """A matcher that matches the all of the patterns given"""


class Many(OptionsMatcher):
    """A matcher that repeatedly matches any of the options"""


class Words(object):
    """A matcher that matches any sequence of letters and spaces"""
    letters = string.uppercase + string.lowercase + " .,"

    def __init__(self, letters=None):
        if letters:
            self.letters = letters

    def __repr__(self):
        return "<%s letters=%r>" % (self.__class__.__name__, self.letters)


class Optional(PatternMatcher):
    """A matcher that matches the pattern if it's available"""


class Indented(PatternMatcher):
    """A matcher that removes indentation from the text before matching the pattern"""
    def __init__(self, pattern, optional=False, initial_indent=None):
        self.pattern = pattern
        self.optional = optional
        self.initial_indent = initial_indent


class Escaped(PatternMatcher):
    """A matcher that html-escapes the text it matches"""


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

def match_all_of(text, pattern, name):
    "Match each of the patterns in pattern"
    result = [name]
    rest = text
    for sub_pattern in pattern.options:
        match, rest = do_parse(rest, sub_pattern)
        if match:
            _add_match_to_result(result, match)
    if result == [name]:
        result.append("")
    return (result, rest)

def match_ignore(text, pattern, name):
    "Match the pattern, but return no result"
    try:
        match, rest = do_parse(text, pattern.pattern)
        return ([], rest)
    except NoPatternFound:
        raise NoPatternFound

def match_one_of(text, pattern, name):
    """Match one of the patterns given"""
    for sub_pattern in pattern.options:
        try:
            match, rest = do_parse(text, sub_pattern)
            result = [name]
            if utils.deep_bool(match):
                _add_match_to_result(result, match)
            else:
                result.append("")
            return (result, rest)
        except NoPatternFound:
            continue
    raise NoPatternFound

def match_count_of(text, pattern, name):
    result = [name]
    rest = text
    for i in range(pattern.count):
        try:
            match, rest = do_parse(rest, pattern.pattern)
        except NoPatternFound:
            raise NoPatternFound("Only %s of the given pattern were found" % i)
        else:
            if match:
                _add_match_to_result(result, match)
    return (result, rest)

def match_insert(text, pattern, name):
    return ([name, pattern.text], text)

def match_join(text, pattern, name):
    try:
        match, rest = do_parse(text, pattern.pattern)
    except NoPatternFound:
        raise NoPatternFound
    result = [name]
    _add_match_to_result(result, match)
    result = filter_match(result)
    return (result, rest)

def filter_match(match, recursive=False):
    "Concatenates consecutive characters"
    result = []
    result.append(match[0])
    submatches = []
    for item in match[1:]:
        if isinstance(item, basestring):
            submatches.append(item)
        else:
            if recursive:
                submatches.append(filter_match(item, recursive=True)[1])
            elif submatches:
                result.append("".join(submatches))
                submatches = []
                result.append(item)
    if submatches:
        result.append("".join(submatches))
    return result

def match_many(text, pattern, name):
    """Repeatedly match any of the given patterns"""
    result = [name]
    rest = text
    match_made = False
    while rest:
        for sub_pattern in pattern.options:
            try:
                match, rest = do_parse(rest, sub_pattern)
                match_made = True
                if utils.deep_bool(match):
                    _add_match_to_result(result, match)
                break
            except NoPatternFound:
                continue
        else:
            break
    if not match_made:
        raise NoPatternFound
    else:
        if result == [name]:
            result.append("")
        return (result, rest)

def match_not(text, pattern, name):
    """Match a character if text doesn't start with pattern"""
    if (not text) or text.startswith(pattern.pattern):
        raise NoPatternFound
    else:
        return ([name, text[0]], text[1:])

def match_optional(text, pattern, name):
    """Match pattern if it's there"""
    try:
        return do_parse(text, pattern.pattern)
    except NoPatternFound:
        return ([], text)

def _get_current_indentation(text, pattern=None):
    "Finds the current number of spaces at the start"
    if pattern and pattern.initial_indent:
        try:
            match, rest = do_parse(text, pattern.initial_indent)
        except NoPatternFound:
            raise NoPatternFound
        match = filter_match(match, recursive=True)
        match = "".join(match[1:])
        if set(match) == set("\t"):
            indent_type = "\t"
        else:
            indent_type = " "
        indent = indent_type * len(match)
        rest = indent + rest
        return (indent, rest)
    else:
        indent = ""
        for char in text:
            if char in [" ", "\t"]:
                if (not indent) or (char in indent):
                    indent = indent + char
            else:
                return (indent, text)
        return (indent, text)

def match_indented(text, pattern, name):
    """Remove indentation before matching"""
    indent, text = _get_current_indentation(text, pattern)
    if (not indent) and (not pattern.optional):
        raise NoPatternFound
    lines = text.split("\n")
    indented_lines = _get_indented_lines(lines, indent)
    other_lines = lines[len(indented_lines):]
    indented_text = "\n".join(indented_lines)
    other_rest = "\n".join(other_lines)
    try:
        indented_match, indented_rest = do_parse(indented_text, pattern.pattern)
    except NoPatternFound:
        raise NoPatternFound
    if indented_rest and other_rest:
        rest = indented_rest + "\n" + other_rest
    else:
        rest = indented_rest + other_rest
    result = [name]
    _add_match_to_result(result, indented_match)
    if len(result) == 1:
        result = result[0]
    return (result, rest)

def _get_indented_lines(lines, indent):
    indented_lines = []
    current_linebreak = []
    for line in lines:
        if line.startswith(indent):
            if current_linebreak:
                indented_lines.extend(current_linebreak)
                current_linebreak = []
            indented_lines.append(line[len(indent):])
        elif (not line) and (not current_linebreak):
            # if the line is blank but the previous line wasn't
            current_linebreak.append(line)
        else:
            break
    return indented_lines

def do_escape(tree):
    """Recursively html escape a parse tree"""
    if isinstance(tree, (list, tuple)):
        name = tree[0]
        result = [name]
        for item in tree[1:]:
            result.append(do_escape(item))
        return result
    else:
        return cgi.escape(tree)

def match_escaped(text, pattern, name):
    """Match the pattern and html escape the result"""
    try:
        match, rest = do_parse(text, pattern.pattern)
    except NoPatternFound:
        raise NoPatternFound
    result = [name]
    escaped_match = do_escape(match)
    _add_match_to_result(result, escaped_match)
    return (result, rest)

def _add_match_to_result(result, match):
    "If the match has no name, extend the result"
    if (not match[0]) or (match[0] == "<lambda>") or match[0].startswith("_"):
        result.extend(match[1:])
    else:
        result.append(match)

matchers = {
    str: match_text,
    unicode: match_text,
    AllOf: match_all_of,
    Some: match_some,
    Words: match_words,
    Ignore: match_ignore,
    OneOf: match_one_of,
    Many: match_many,
    Not: match_not,
    Optional: match_optional,
    Indented: match_indented,
    Escaped: match_escaped,
    Insert: match_insert,
    CountOf: match_count_of,
    Join: match_join,
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
    return (pattern, pattern_name, pattern_type)
