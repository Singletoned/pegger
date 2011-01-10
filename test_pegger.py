# -*- coding: utf-8 -*-

from pegger import parse_string

def test_parse_string_a():
    def letter_a():
        return "a"

    result = parse_string("a", letter_a)
    assert result == ['letter_a', "a"]

    result = parse_string("c", letter_a)
    assert result == None

def test_parse_string_b():
    def letter_b():
        return "b"

    result = parse_string("b", letter_b)
    assert result == ['letter_b', "b"]

    result = parse_string("c", letter_b)
    assert result == None

def test_parse_string_ab():
    def letter_a():
        return "a"

    def letter_b():
        return "b"

    def word_ab():
        return (letter_a, letter_b)

    result = parse_string("ab", word_ab)
    assert result == [['letter_a', "a"], ['letter_b', "b"]]

