# -*- coding: utf-8 -*-

import string
import cgi

import utils


class NoPatternFound(Exception):
    pass

class UnknownMatcherType(Exception):
    def __init__(self, pattern_type):
        self.pattern_type = pattern_type

    def __str__(self):
        return "%s was not found" % self.pattern_type

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


class NamedPattern(object):
    """A pattern with a name"""
    def __init__(self, name, pattern):
        self.name = name
        self.pattern = pattern


class BasePatternCreator(object):
    def __call__(self, text, name=""):
        return self.match(text, name)

    def __repr__(self):
        return "<%s>" % (self.__class__.__name__)


class PatternCreator(BasePatternCreator):
    """A pattern creator"""
    def __init__(self, pattern):
        self.pattern = pattern

    def __repr__(self):
        return "<%s pattern=%r>" % (self.__class__.__name__, self.pattern)


class OptionsPatternCreator(BasePatternCreator):
    """A pattern creator with a list of options"""
    def __init__(self, *options):
        self.options = options

    def __repr__(self):
        return "<%s options=%r>" % (self.__class__.__name__, self.options)


class Some(PatternCreator):
    """Match the given char repeatedly"""
    def match(self, text, name=""):
        match = []
        rest = list(text)
        while rest:
            char = rest[0]
            if self.pattern == char:
                match.append(rest.pop(0))
            else:
                break
        if not match:
            raise NoPatternFound
        return ([name, "".join(match)], "".join(rest))


class Words(PatternCreator):
    "Match everything that is part of pattern.letters"
    letters = string.uppercase + string.lowercase + " .,"

    def __init__(self, letters=None):
        if letters:
            self.letters = letters

    def __repr__(self):
        return "<%s letters=%r>" % (self.__class__.__name__, self.letters)

    def match(self, text, name):
        match = []
        rest = list(text)
        while rest:
            char = rest[0]
            if char in self.letters:
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

class Ignore(PatternCreator):
    "Match the pattern, but return no result"
    def match(self, text, name):
        try:
            match, rest = do_parse(text, self.pattern)
            return ([], rest)
        except NoPatternFound:
            raise NoPatternFound


class AllOf(OptionsPatternCreator):
    "Match each of the patterns in pattern"
    def match(self, text, name):
        result = [name]
        rest = text
        for sub_pattern in self.options:
            match, rest = do_parse(rest, sub_pattern)
            if match:
                _add_match_to_result(result, match)
        if result == [name]:
            result.append("")
        return (result, rest)


class OneOf(OptionsPatternCreator):
    """Match one of the patterns given"""
    def match(self, text, name):
        for sub_pattern in self.options:
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


class CountOf(PatternCreator):
    """A matcher that matches count items"""
    def __init__(self, count, pattern):
        self.count = count
        self.pattern = pattern

    def match(self, text, name):
        result = [name]
        rest = text
        for i in range(self.count):
            try:
                match, rest = do_parse(rest, self.pattern)
            except NoPatternFound:
                raise NoPatternFound("Only %s of the given pattern were found" % i)
            else:
                if match:
                    _add_match_to_result(result, match)
        return (result, rest)


class Insert(PatternCreator):
    """A matcher that inserts some text into the result"""
    def __init__(self, text):
        self.text = text

    def match(self, text, name):
        return ([name, self.text], text)

    def __repr__(self):
        return "<%s text=%r>" % (self.__class__.__name__, self.text)


class EOF(BasePatternCreator):
    """A matcher that matches the end of the string"""
    def match(self, text, name):
        if not text:
            return ([name, ''], text)
        else:
            raise NoPatternFound("No EOF found")


class Join(PatternCreator):
    def match(self, text, name):
        try:
            match, rest = do_parse(text, self.pattern)
        except NoPatternFound:
            raise NoPatternFound
        result = [name]
        _add_match_to_result(result, match)
        result = filter_match(result)
        return (result, rest)

def filter_match(match, recursive=False):
    "Concatenates consecutive characters"
    if match == []:
        return match
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


class Many(OptionsPatternCreator):
    """Repeatedly match any of the given patterns"""
    def match(self, text, name):
        result = [name]
        rest = text
        match_made = False
        while rest:
            for sub_pattern in self.options:
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


class Not(PatternCreator):
    """Match a character if text doesn't start with pattern"""
    def match(self, text, name):
        if not text:
            raise NoPatternFound
        try:
            match, rest = do_parse(text, self.pattern)
        except NoPatternFound:
            return ([name, text[0]], text[1:])
        else:
            raise NoPatternFound


class Optional(PatternCreator):
    """A matcher that matches the pattern if it's available"""
    def match(self, text, name):
        """Match pattern if it's there"""
        try:
            return do_parse(text, self.pattern)
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
    elif pattern and pattern.indent_pattern:
        indent, rest = do_parse(text, pattern.indent_pattern)
        indent = indent[1]
        return (indent, text)
    else:
        indent = ""
        for char in text:
            if char in [" ", "\t"]:
                if (not indent) or (char in indent):
                    indent = indent + char
            else:
                return (indent, text)
        return (indent, text)


class Indented(PatternCreator):
    """Remove indentation before matching"""
    def __init__(self, pattern, optional=False, initial_indent=None, indent_pattern=None):
        self.pattern = pattern
        self.optional = optional
        self.initial_indent = initial_indent
        self.indent_pattern = indent_pattern

    def match(self, text, name):
        indent, text = _get_current_indentation(text, self)
        if (not indent) and (not self.optional):
            raise NoPatternFound
        lines = text.split("\n")
        indented_lines = _get_indented_lines(lines, indent)
        other_lines = lines[len(indented_lines):]
        indented_text = "\n".join(indented_lines)
        try:
            indented_match, indented_rest = do_parse(indented_text, self.pattern)
        except NoPatternFound:
            raise NoPatternFound
        indented_rest = indented_rest.replace("\n", "\n"+indent)
        rest_lines = [line for line in indented_rest.split("\n")]
        rest_lines = rest_lines + other_lines
        rest = "\n".join(rest_lines)
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


class Escaped(PatternCreator):
    """Match the pattern and html escape the result"""
    def match(self, text, name):
        try:
            match, rest = do_parse(text, self.pattern)
        except NoPatternFound:
            raise NoPatternFound
        result = [name]
        escaped_match = do_escape(match)
        _add_match_to_result(result, escaped_match)
        return (result, rest)


class Lookahead(PatternCreator):
    """Match the pattern somewhere ahead and remove it from there"""
    def match(self, text, name):
        unmatched = ""
        while text:
            try:
                match, rest = do_parse(text, self.pattern)
                result = [name]
                _add_match_to_result(result, match)
                return (result, unmatched+rest)
            except NoPatternFound:
                unmatched = unmatched + text[0]
                text = text[1:]
        raise NoPatternFound

def _add_match_to_result(result, match):
    "If the match has no name, extend the result"
    if (not match[0]) or (match[0] == "<lambda>") or match[0].startswith("_"):
        result.extend(match[1:])
    else:
        result.append(match)

matchers = {
    str: match_text,
    unicode: match_text,
    AllOf: lambda text, pattern, pattern_name: pattern(text, pattern_name),
    Some: lambda text, pattern, pattern_name: pattern(text, pattern_name),
    Words: lambda text, pattern, pattern_name: pattern(text, pattern_name),
    Ignore: lambda text, pattern, pattern_name: pattern(text, pattern_name),
    OneOf: lambda text, pattern, pattern_name: pattern(text, pattern_name),
    Many: lambda text, pattern, pattern_name: pattern(text, pattern_name),
    Not: lambda text, pattern, pattern_name: pattern(text, pattern_name),
    Optional: lambda text, pattern, pattern_name: pattern(text, pattern_name),
    Indented: lambda text, pattern, pattern_name: pattern(text, pattern_name),
    Escaped: lambda text, pattern, pattern_name: pattern(text, pattern_name),
    Insert: lambda text, pattern, pattern_name: pattern(text, pattern_name),
    CountOf: lambda text, pattern, pattern_name: pattern(text, pattern_name),
    Join: lambda text, pattern, pattern_name: pattern(text, pattern_name),
    EOF: lambda text, pattern, pattern_name: pattern(text, pattern_name),
    }

def do_parse(text, pattern):
    """Dispatch to the correct function based on the type of the pattern"""
    if isinstance(pattern, BasePatternCreator):
        return pattern(text)
    else:
        pattern, pattern_name, pattern_type = get_pattern_info(pattern)
        try:
            matcher_func = matchers[pattern_type]
            result = matcher_func(text, pattern, pattern_name)
            return result
        except KeyError:
            raise UnknownMatcherType(pattern_type)

def parse_string(text, pattern):
    match, rest = do_parse(text, pattern)
    return match

def get_pattern_info(pattern):
    pattern_name = ""
    if isinstance(pattern, NamedPattern):
        pattern_name = pattern.name
        pattern = pattern.pattern
    elif callable(pattern):
        pattern_name = pattern.__name__
        pattern = pattern()
        if pattern_name == "<lambda>":
            pattern_name = ""
    pattern_type = type(pattern)
    return (pattern, pattern_name, pattern_type)
