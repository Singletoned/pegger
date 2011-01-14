# -*- coding: utf-8 -*-

import py

import pegger as pg


def test_match_some():
    def word_a():
        return pg.Some('a')

    match, rest = pg.match_some("a", word_a)
    assert match == ['word_a', "a"]
    assert rest == ""

    match, rest = pg.match_some("aab", word_a)
    assert match == ['word_a', "aa"]
    assert rest == "b"

    with py.test.raises(pg.NoPatternFound):
        match, rest = pg.match_some("ccc", word_a)

def test_match_text():
    """Test that a text pattern removes the pattern from the beginning
    of the text and returns the rest"""

    def letter_a():
        return "a"
    
    result = pg.match_text("ab", letter_a)
    assert result == (['letter_a', "a"], "b")

    result = pg.match_text("aabc", letter_a)
    assert result == (['letter_a', "a"], "abc")

    with py.test.raises(pg.NoPatternFound):
        match, rest = pg.match_text("ccc", letter_a)

def test_match_tuple():
    def letter_a():
        return "a"

    def letter_b():
        return "b"

    def word_ab():
        return (letter_a, letter_b)

    match, rest = pg.match_tuple("ab", word_ab)
    assert match == ['word_ab', [['letter_a', "a"], ['letter_b', "b"]]]
    assert rest == ""
    # assert result == ([['letter_a', "a"], ['letter_b', "b"]], "")

    with py.test.raises(pg.NoPatternFound):
        result = pg.match_tuple("cab", word_ab)

def test_match_ignore():
    def ignore_a():
        return pg.Ignore("a")

    match, rest = pg.match_ignore("a", ignore_a)
    assert match == []
    assert rest == ""

def test_match_one_of():
    def emphasis():
        return (
            lambda: pg.Ignore("*"),
            lambda: pg.Words(),
            lambda: pg.Ignore("*"))

    def words():
        return pg.Words()

    def phrase():
        return pg.OneOf(
            words,
            emphasis)

    match, rest = pg.match_one_of("*bold*", phrase)
    
def test_parse_string_a():
    def letter_a():
        return "a"

    result = pg.parse_string("a", letter_a)
    assert result == ['letter_a', "a"]

    result = pg.parse_string("ab", letter_a)
    assert result == ['letter_a', "a"]

    with py.test.raises(pg.NoPatternFound):
        result = pg.parse_string("c", letter_a)

def test_parse_string_b():
    def letter_b():
        return "b"

    result = pg.parse_string("b", letter_b)
    assert result == ['letter_b', "b"]

    with py.test.raises(pg.NoPatternFound):
        result = pg.parse_string("c", letter_b)

def test_parse_string_ab():
    def letter_a():
        return "a"

    def letter_b():
        return "b"

    def word_ab():
        return (letter_a, letter_b)

    result = pg.parse_string("ab", word_ab)
    assert result == ['word_ab', [['letter_a', "a"], ['letter_b', "b"]]]

    with py.test.raises(pg.NoPatternFound):
        result = pg.parse_string("cab", word_ab)

def test_parse_string_some_a():
    def word_a():
        return pg.Some('a')

    result = pg.parse_string("aa", word_a)
    assert result == ['word_a', "aa"]

    result = pg.parse_string("aaa", word_a)
    assert result == ['word_a', "aaa"]

    with py.test.raises(pg.NoPatternFound):
        result = pg.parse_string("caa", word_a)

def test_parse_string_some_aab():
    def word_a():
        return pg.Some('a')

    def letter_b():
        return "b"

    def word_aab():
        return (word_a, letter_b)

    result = pg.parse_string("aab", word_aab)
    assert result == ['word_aab', [['word_a', "aa"], ['letter_b', "b"]]]

    with py.test.raises(pg.NoPatternFound):
        result = pg.parse_string("caab", word_aab)

def test_parse_words():
    def body():
        return pg.Words()

    result = pg.parse_string("The confused dog jumped over the fox", body)
    assert result == ['body', "The confused dog jumped over the fox"]

def test_parse_ignore():
    def emphasis():
        return (
            lambda: pg.Ignore("*"),
            lambda: pg.Words(),
            lambda: pg.Ignore("*"))

    result = pg.parse_string("*bold words*", emphasis)
    assert result == ['emphasis', "bold words"]

def test_parse_one_of():
    def emphasis():
        return (
            lambda: pg.Ignore("*"),
            lambda: pg.Words(),
            lambda: pg.Ignore("*"))

    def words():
        return pg.Words()

    def phrase():
        return pg.OneOf(
            words,
            emphasis)

    result = pg.parse_string("*bold words*", phrase)
    assert result == ['emphasis', "bold words"]

    result = pg.parse_string("normal words", phrase)
    assert result == ['words', "normal words"]

def test_unknown_matcher():
    def unknown():
        return 1

    with py.test.raises(pg.UnknownMatcherType):
        result = pg.parse_string("", unknown)
