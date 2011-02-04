# -*- coding: utf-8 -*-

import string

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


class Some(PatternMatcher):
    """A matcher that matches any one char repeatedly"""


class Ignore(PatternMatcher):
    """A matcher that matches any one char repeatedly"""


class Not(PatternMatcher):
    """A matcher that matches any string that isn't the pattern"""


class OneOf(OptionsMatcher):
    """A matcher that matches the first matching matcher"""


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
    if not name:
        return ("".join(match), "".join(rest))
    else:
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
    result = [name]
    rest = text
    for sub_pattern in pattern:
        match, rest = do_parse(rest, sub_pattern)
        if match:
            if not match[0]:
                result.extend(match[1:])
            else:
                result.append(match)
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
        except NoPatternFound:
            continue
        if match:
            if (not match) or (match[0] == "<lambda>"):
                match = match[1]
            return (match, rest)
    raise NoPatternFound

def match_many(text, pattern, name):
    """Repeatedly match any of the given patterns"""
    result = [name]
    rest = text
    while rest:
        match_made = False
        for sub_pattern in pattern.options:
            try:
                match, rest = do_parse(rest, sub_pattern)
            except NoPatternFound:
                continue
            if match:
                match_made = True
                if (not match[0]) or (match[0] == "<lambda>"):
                    result.extend(match[1:])
                else:
                    result.append(match)
        if not match_made:
            break
    if result == [name]:
        raise NoPatternFound
    else:
        return (result, rest)

def match_not(text, pattern, name):
    """Match any string that is not the pattern"""
    match = []
    rest = text
    while rest:
        if rest.startswith(pattern.pattern):
            break
        else:
            match.append(rest[0])
            rest = rest[1:]
    if not match:
        raise NoPatternFound
    else:
        return ([name, "".join(match)], rest)

def match_optional(text, pattern, name):
    """Match pattern if it's there"""
    try:
        return do_parse(text, pattern.pattern)
    except NoPatternFound:
        return ([], text)

def match_indented(text, pattern, name):
    """Remove indentation before matching"""
    if text.startswith("\n"):
        text = text[1:]
    else:
        # This isn't the begining of a line
        raise NoPatternFound
    indent = ""
    # Find the current level of indentation
    for char in text:
        if char == " ":
            indent = indent + char
        else:
            break
    if not indent:
        raise NoPatternFound
    lines = text.split("\n")
    other_lines = list(lines)
    indented_lines = []
    for line in lines:
        if line.startswith(indent):
            unindented_line = other_lines.pop(0)[len(indent):]
            indented_lines.append(unindented_line)
        else:
            break
    indented_text = "\n" + "\n".join(indented_lines)
    other_rest = "\n".join(other_lines)
    try:
        indented_match, indented_rest = do_parse(indented_text, pattern.pattern)
    except NoPatternFound:
        raise NoPatternFound
    rest = indented_rest + "\n" + other_rest
    if name:
        return ([name, indented_match], rest)
    else:
        return indented_match, rest

matchers = {
    str: match_text,
    unicode: match_text,
    tuple: match_tuple,
    Some: match_some,
    Words: match_words,
    Ignore: match_ignore,
    OneOf: match_one_of,
    Many: match_many,
    Not: match_not,
    Optional: match_optional,
    Indented: match_indented,
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

lookups = {
    '': None,
    'nested_list': "ol",
    'ordered_list': "ol",
    'list_item': "li",
    'body': "body",
    'numbered_bullet': "li",
    'plain': None,
    'emphasis': "strong",
    'code': "code",
    'link_text': None,
    'link_url': None,
    'link': "a",
    }

def indent_tags(data):
    result = []
    for item in data:
        result.append("  "+item)
    return result

def make_block(head, rest):
    tag = lookups[head]
    start_tag = "<%s>" % tag
    end_tag = "</%s>" % tag
    content = []
    for item in rest:
        content.extend(do_render(item))
    content = indent_tags(content)
    return [start_tag] + content + [end_tag]

def make_span(head, rest):
    tag = lookups[head]
    if tag:
        start_tag = "<%s>" % tag
        end_tag = "</%s>" % tag
    else:
        start_tag = ""
        end_tag = ""
    content = []
    for item in rest:
        content.extend(do_render(item))
    content = "".join(content)
    return ["%s%s%s" % (start_tag, content, end_tag)]

def make_tagless(head, rest):
    content = []
    for item in rest:
        content.extend(do_render(item))
    return content

def make_anchor(head, rest):
    link_text, link_url = rest
    link_text = do_render(link_text)
    link_url = link_url[1]
    link_template = '''<a href="%s">%s</a>'''
    result = link_template % (link_url, "".join(link_text))
    return [result]

tag_funcs = {
    'list_item': make_block,
    'emphasis': make_span,
    'ordered_list': make_block,
    'code': make_span,
    '': make_tagless,
    'nested_list': make_block,
    'plain': make_span,
    'link': make_anchor,
    'link_text': make_span,
    }

def do_render(data):
    if isinstance(data, basestring):
        return [data]
    else:
        head, rest = data[0], data[1:]
        func = tag_funcs[head]
        return func(head, rest)

def htmlise(node, depth=0):
    return "\n".join(do_render(node))
