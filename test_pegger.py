# -*- coding: utf-8 -*-

from pegger import parse_string

def test_parse_string_a():
    def letter_a():
        return "a"

    result = parse_string("a", letter_a)
    assert result == ['letter_a', "a"]
