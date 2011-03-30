# -*- coding: utf-8 -*-

import py

import pegger as pg


def test_match_some():
    word_a = pg.Some('a')

    match, rest = pg.match_some("a", word_a, "word_a")
    assert match == ['word_a', "a"]
    assert rest == ""

    match, rest = pg.match_some("aab", word_a, "word_a")
    assert match == ['word_a', "aa"]
    assert rest == "b"

    with py.test.raises(pg.NoPatternFound):
        match, rest = pg.match_some("ccc", word_a, "word_a")

def test_match_text():
    """Test that a text pattern removes the pattern from the beginning
    of the text and returns the rest"""

    letter_a = "a"

    match, rest = pg.match_text("ab", letter_a, "letter_a")
    assert match == ['letter_a', "a"]
    assert rest == "b"

    match, rest = pg.match_text("aabc", letter_a, "letter_a")
    assert match == ['letter_a', "a"]
    assert rest == "abc"

    with py.test.raises(pg.NoPatternFound):
        match, rest = pg.match_text("ccc", letter_a, "letter_a")

def test_match_words():
    """Test that Words matches letters and punctuation"""
    plain = pg.Words()

    match, rest = pg.match_words("some words", plain, 'plain')
    assert match == ['plain', "some words"]
    assert rest == ""

    # Match with no name
    match, rest = pg.match_words("some words", plain, '')
    assert match == ['', "some words"]
    assert rest == ""

    match, rest = pg.match_words("some words 123", plain, 'plain')
    assert match == ['plain', "some words "]
    assert rest == "123"

    match, rest = pg.match_words("Some words, and punctuation.", plain, 'plain')
    assert match == ['plain', "Some words, and punctuation."]
    assert rest == ""


def test_match_all_of():
    def letter_a():
        return "a"

    def letter_b():
        return "b"

    word_ab = pg.AllOf(letter_a, letter_b)

    match, rest = pg.match_all_of("ab", word_ab, "word_ab")
    assert match == ['word_ab', ['letter_a', "a"], ['letter_b', "b"]]
    assert rest == ""

    word_abc = pg.AllOf(letter_a, pg.Words())

    expected = ['word_ab', ['letter_a', "a"], "bc"]
    match, rest = pg.match_all_of("abc", word_abc, "word_ab")
    assert match == expected
    assert rest == ""

    match, rest = pg.match_all_of("abc!", word_abc, "")
    assert match == ['', ['letter_a', "a"], "bc"]
    assert rest == "!"

    emphasis = pg.AllOf(
        lambda: pg.Ignore("*"),
        lambda: pg.Words(),
        lambda: pg.Ignore("*"))

    match, rest = pg.match_all_of("*abc*", emphasis, "emphasis")
    assert match == ['emphasis', "abc"]

    with py.test.raises(pg.NoPatternFound):
        result = pg.match_all_of("cab", word_ab, "word_ab")

def test_match_ignore():
    ignore_a = pg.Ignore("a")

    match, rest = pg.match_ignore("a", ignore_a, "ignore_a")
    assert match == []
    assert rest == ""

    ignore_a = pg.Ignore(
        pg.AllOf(pg.Optional("#"),
         "abc"))

    match, rest = pg.match_ignore("#abc", ignore_a, "ignore_a")
    assert match == []
    assert rest == ""

    with py.test.raises(pg.NoPatternFound):
        match, rest = pg.match_ignore("123", ignore_a, "ignore_a")

def test_match_one_of():
    emphasis = pg.AllOf(
        pg.Ignore("*"),
        lambda: pg.Many(pg.Not("*")),
        pg.Ignore("*"))

    phrase = pg.OneOf(
            pg.Words(),
            emphasis)

    expected = ['phrase', "b", "o", "l", "d"]
    match, rest = pg.match_one_of("*bold*", phrase, "phrase")
    assert match == expected
    assert rest == ""

    with py.test.raises(pg.NoPatternFound):
        match, rest = pg.match_one_of("123", phrase, "phrase")

    match, rest = pg.match_one_of("text", phrase, "phrase")
    assert match == ['phrase', "text"]
    assert rest == ""

    # Test match with no name
    match, rest = pg.match_one_of("text", phrase, "")
    assert match == ['', "text"]
    assert rest == ""

def test_match_many_simple():
    def a():
        return "a"

    def b():
        return "b"

    letters = pg.Many(a, b)

    expected = ['letters', ['a', "a"], ['b', "b"], ['a', "a"], ['b', "b"]]
    match, rest = pg.match_many("abab", letters, "letters")
    assert match == expected
    assert rest == ""

    match, rest = pg.match_many("ababcc", letters, "letters")
    assert match == ['letters', ['a', "a"], ['b', "b"], ['a', "a"], ['b', "b"]]
    assert rest == "cc"

    match, rest = pg.match_many("ababcc", letters, "")
    assert match == ['', ['a', "a"], ['b', "b"], ['a', "a"], ['b', "b"]]
    assert rest == "cc"

    with py.test.raises(pg.NoPatternFound):
        match, rest = pg.match_many("cab", letters, "letters")

def test_match_many_complex():
    def emphasis():
        return pg.AllOf(
            lambda: pg.Ignore("*"),
            lambda: pg.Words(),
            lambda: pg.Ignore("*"))

    def words():
        return pg.Words()

    body = pg.Many(emphasis, words)

    expected = [
        'body',
        ['words', 'a phrase with '],
         ['emphasis', "bold words"],
         ['words', " in it"]]
    match, rest = pg.match_many("a phrase with *bold words* in it", body, 'body')
    assert match == expected
    assert rest == ""

def test_match_many_specificty():
    def lettter_a():
        return "a"

    def lettter_b():
        return "b"

    def other_letters():
        return pg.Words()

    match_letters = pg.Many(
        lettter_a,
        lettter_b,
        other_letters)

    data = "abac"

    expected = [
        'match_letters',
        ['lettter_a', "a"],
        ['lettter_b', "b"],
        ['lettter_a', "a"],
        ['other_letters', "c"]]

    match, rest = pg.match_many(data, match_letters, 'match_letters')
    assert match == expected
    assert rest == ""

def test_match_join():
    three_times_a = pg.Join(
        pg.CountOf(
            3, "a"))

    data = "aaa"
    expected = ['three_times_a', "aaa"]
    match, rest = pg.match_join(data, three_times_a, 'three_times_a')
    assert match == expected
    assert rest == ""

    not_d = pg.Join(
        pg.Many(
            pg.Not("d")))

    data = "abcd"
    expected = ['not_d', "abc"]
    match, rest = pg.match_join(data, not_d, 'not_d')
    assert match == expected
    assert rest == "d"

def test_filter_match():
    data = ['foo', "bar", "baz"]
    expected = ['foo', "barbaz"]
    result = pg.filter_match(data)
    assert result == expected

    data = ['foo', "bar", "baz", ['flib', "flamble"], "bar", "ington"]
    expected = ['foo', "barbaz", ['flib', "flamble"], "barington"]
    result = pg.filter_match(data)
    assert result == expected

    data = ['foo', "bar", "baz", ['flib', "flamble"], "bar", "ington"]
    expected = ['foo', "barbazflamblebarington"]
    result = pg.filter_match(data, recursive=True)
    assert result == expected

def test_match_count_of():
    three_dashes = pg.CountOf(3, "-")

    with py.test.raises(pg.NoPatternFound):
        match, rest = pg.match_count_of("--", three_dashes, 'three_dashes')

    expected = [
        'three_dashes',
        "-", "-", "-"]

    match, rest = pg.match_count_of("---", three_dashes, 'three_dashes')
    assert match == expected
    assert rest == ""

    expected = [
        'three_dashes',
        "-", "-", "-"]

    match, rest = pg.match_count_of("----", three_dashes, 'three_dashes')
    assert match == expected
    assert rest == "-"

def test_match_insert():
    insert_a = pg.Insert("a")

    expected = ['insert_a', "a"]

    match, rest = pg.match_insert("", insert_a, 'insert_a')
    assert match == expected
    assert rest == ""

    joined_lines = pg.AllOf(
        pg.Ignore("\n"),
        pg.Words(),
        pg.Insert(" : "),
        pg.Ignore("\n"),
        pg.Words())

    data = """
flamble
floosit"""

    expected = [
        "joined_lines",
        'flamble',
        " : ",
        'floosit']

    match, rest = pg.match_all_of(data, joined_lines, 'joined_lines')
    assert match == expected
    assert rest == ""

def test_match_not():
    not_a = pg.Not("a")

    match, rest = pg.match_not("b", not_a, 'not_a')
    assert match == ['not_a', "b"]
    assert rest == ""

    match, rest = pg.match_not("ba", not_a, 'not_a')
    assert match == ['not_a', "b"]
    assert rest == "a"

    with py.test.raises(pg.NoPatternFound):
        match, rest = pg.match_not("abc", not_a, 'not_a')

    match, rest = pg.match_not("bcd", not_a, 'not_a')
    assert match == ['not_a', "b"]
    assert rest == "cd"

def test_match_optional():
    optional_a = pg.Optional("a")

    match, rest = pg.match_optional("abc", optional_a, 'optional_a')
    assert match == ['', "a"]
    assert rest == "bc"

    match, rest = pg.match_optional("bc", optional_a, 'optional_a')
    assert match == []
    assert rest == "bc"

    def letter_a():
        return "a"

    optional_a = pg.Optional(letter_a)
    match, rest = pg.match_optional("abc", optional_a, 'optional_a')
    assert match == ['letter_a', "a"]
    assert rest == "bc"

    optional_ignore = pg.Optional(pg.Ignore("a"))

    match, rest = pg.match_optional("abc", optional_ignore, 'optional_ignore')
    assert match == []
    assert rest == "bc"

def test_match_indented():
    # Test without optional

    def list_item():
        return (
            pg.Ignore("\n* "),
            pg.Words())

    indented_bullets = pg.Indented(
        pg.Many(list_item))

    data = """
* A bullet"""

    expected = [
        'list_item', "A bullet"]

    with py.test.raises(pg.NoPatternFound):
        match, rest = pg.match_indented(data, indented_bullets, 'indented_bullets')

    # Test with optional

    def list_item():
        return pg.AllOf(
            pg.Ignore("* "),
            pg.Words())

    indented_bullets = pg.Indented(
        pg.Many(list_item),
        optional=True)

    data = """* A bullet"""

    expected = [
        'indented_bullets',
        ['list_item', "A bullet"]]

    match, rest = pg.match_indented(data, indented_bullets, 'indented_bullets')
    assert match == expected
    assert rest == "\n"

    def paragraph():
        return (
            pg.Words())

    indented_text = pg.Indented(paragraph)

    data_with_spaces = """  Some text"""
    data_with_tabs = """\tSome text"""

    expected = [
        'indented_text',
        ['paragraph', "Some text"]]

    for data in [data_with_spaces, data_with_tabs]:
        match, rest = pg.match_indented(data, indented_text, 'indented_text')
        assert match == expected
        assert rest == "\n"

    # Check indented with unnamed subpattern

    data = "  Some text"

    paragraph = (
        pg.Words())

    indented_text = pg.Indented(paragraph)

    expected = [
        'indented_text',
        "Some text"]

    match, rest = pg.match_indented(data, indented_text, 'indented_text')
    assert match == expected
    assert rest == "\n"

    # Check indented with unnamed pattern and unnamed subpattern

    expected = [None, "Some text"]

    match, rest = pg.match_indented(data, indented_text, None)
    assert match == expected
    assert rest == "\n"

def test_match_indented_nested_bullets():
    def bullet():
        return pg.AllOf(
            pg.Ignore(
                pg.Optional(
                    pg.Many("\n"))),
            pg.Ignore("* "),
            pg.Words())

    def indented_bullets():
        return pg.Indented(
            pg.AllOf(
                bullet,
                pg.Optional(
                    indented_bullets,
                    )),
            optional=True)

    data = """
* Line One
* Line Two
"""

    expected = [
        'indented_bullets',
        ['bullet', "Line One"],
        ['indented_bullets',
         ['bullet', "Line Two"]]]

    match, rest = pg.match_indented(data, indented_bullets(), 'indented_bullets')
    assert match == expected
    assert rest == "\n\n\n"

def test_indented_bullet():
    def paragraph():
        return pg.AllOf(
            pg.Ignore(pg.Optional("\n")),
            pg.Words())

    indented_paragraphs =  pg.Indented(
        pg.Many(paragraph),
        initial_indent="*   ")

    data = """
*   Paragraph One
    Paragraph Two
""".strip()

    expected = [
        'indented_paragraphs',
        ['paragraph',
         "Paragraph One"],
        ['paragraph',
         "Paragraph Two"]]

    match, rest = pg.match_indented(data, indented_paragraphs, "indented_paragraphs")
    assert match == expected

def test_match_escaped():
    def html_text():
        return pg.Many(
            pg.Words(
                pg.Words.letters + "</>"))

    escaped_text = pg.Escaped(html_text)

    data = """<p>Some text</p>"""

    expected = [
        'escaped_text',
        ['html_text', "&lt;p&gt;Some text&lt;/p&gt;"]]

    match, rest = pg.match_escaped(data, escaped_text, 'escaped_text')
    assert match == expected
    assert rest == ""

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
        return pg.AllOf(letter_a, letter_b)

    expected = ['word_ab',
                ['letter_a', "a"],
                ['letter_b', "b"]]

    result = pg.parse_string("ab", word_ab)
    assert result == expected

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
        return pg.AllOf(word_a, letter_b)

    expected = ['word_aab',
                ['word_a', "aa"],
                ['letter_b', "b"]]

    result = pg.parse_string("aab", word_aab)
    assert result == expected

    with py.test.raises(pg.NoPatternFound):
        result = pg.parse_string("caab", word_aab)

def test_parse_words():
    def body():
        return pg.Words()

    result = pg.parse_string("The confused dog jumped over the fox", body)
    assert result == ['body', "The confused dog jumped over the fox"]

def test_parse_ignore():
    def emphasis():
        return pg.AllOf(
            lambda: pg.Ignore("*"),
            lambda: pg.Words(),
            lambda: pg.Ignore("*"))

    result = pg.parse_string("*bold words*", emphasis)
    assert result == ['emphasis', "bold words"]

def test_parse_one_of():
    def emphasis():
        return pg.AllOf(
            lambda: pg.Ignore("*"),
            lambda: pg.Words(),
            lambda: pg.Ignore("*"))

    def words():
        return pg.Words()

    def phrase():
        return pg.OneOf(
            words,
            emphasis)

    expected = ['phrase', ['emphasis', "bold words"]]
    result = pg.parse_string("*bold words*", phrase)
    assert result == expected

    expected = ['phrase', ['words', "normal words"]]
    result = pg.parse_string("normal words", phrase)
    assert result == expected

def test_parse_many():
    def emphasis():
        return pg.AllOf(
            lambda: pg.Ignore("*"),
            lambda: pg.Words(),
            lambda: pg.Ignore("*"))

    def words():
        return pg.Words()

    def phrase():
        return pg.OneOf(
            words,
            emphasis)

    def body():
        return pg.Many(phrase)

    expected = ['body',
                ['phrase',
                 ['words', 'a phrase with ']],
                ['phrase',
                 ['emphasis', "bold words"]],
                ['phrase',
                 ['words', " in it"]]]

    result = pg.parse_string("a phrase with *bold words* in it", body)
    assert result == expected

    with py.test.raises(pg.NoPatternFound):
        result = pg.parse_string("123", body)

def test_not():
    def not_a():
        return pg.Not("a")

    result = pg.parse_string("bc", not_a)
    assert result == ['not_a', 'b']

    with py.test.raises(pg.NoPatternFound):
        result = pg.parse_string("a", not_a)

def test_optional():
    def optional_a():
        return pg.Optional("a")

    result = pg.parse_string("a", optional_a)
    expected = ['', "a"]
    assert expected == result


    def optional_a():
        return pg.Optional("a")

    def letters():
        return pg.Words()

    def body():
        return pg.AllOf(optional_a, letters)

    result = pg.parse_string("abc", body)
    expected = [
        'body',
        "a",
        ['letters', "bc"]]
    assert expected == result

def test_indented():
    def list_item():
        return pg.AllOf(
            pg.Ignore(
                pg.Optional(
                    pg.Many("\n"))),
            pg.Ignore("* "),
            pg.Words())

    def nested_list():
        return pg.AllOf(
            pg.Ignore(
                pg.Optional(
                    pg.Many("\n"))),
            pg.Indented(
                pg.AllOf(
                    list_item,
                pg.Optional(
                    pg.Many(
                        list_item,
                        nested_list))),
                optional=True))

    data = """
* A bullet
"""

    expected = [
        'nested_list',
        ['list_item', "A bullet"]]

    result = pg.parse_string(data, nested_list)
    assert expected == result

    data = """
* A bullet
  * A bullet in a sublist
"""

    expected = [
        'nested_list',
        ['list_item', "A bullet"],
        ['nested_list',
         ['list_item', "A bullet in a sublist"]]]

    result = pg.parse_string(data, nested_list)
    assert expected == result

    data = """
* A bullet
  * A bullet in a sublist
  * Another bullet in a sublist
* Another bullet in the first list
"""

    expected = [
        'nested_list',
        ['list_item', "A bullet"],
        ['nested_list',
         ['list_item', "A bullet in a sublist"],
         ['list_item', "Another bullet in a sublist"]],
        ['list_item', "Another bullet in the first list"]]

    result = pg.parse_string(data, nested_list)
    assert expected == result

def test_escaped():
    def html_text():
        return pg.Many(
            pg.Words(
                pg.Words.letters+"</>"))

    def escaped_text():
        return pg.Escaped(html_text)

    data = """<p>Some Text</p>"""

    expected = [
        'escaped_text',
        ['html_text',
         "&lt;p&gt;Some Text&lt;/p&gt;"]]

    result = pg.parse_string(data, escaped_text)
    assert expected == result

    html_text = pg.Many(
        pg.Words(
            pg.Words.letters+"</>"))

    def escaped_text():
        return pg.Escaped(html_text)

    expected = [
        'escaped_text',
        "&lt;p&gt;Some Text&lt;/p&gt;"]

    result = pg.parse_string(data, escaped_text)
    assert expected == result

def test_unknown_matcher():
    def unknown():
        return 1

    with py.test.raises(pg.UnknownMatcherType):
        result = pg.parse_string("", unknown)

def test_get_pattern_info():
    def my_pattern():
        return "123"

    pattern, p_name, p_type = pg.get_pattern_info(my_pattern)
    assert pattern == "123"
    assert p_name == "my_pattern"
    assert p_type == str

    lambda_pattern = lambda: dict()

    pattern, p_name, p_type = pg.get_pattern_info(lambda_pattern)
    assert pattern == dict()
    assert p_name == ""
    assert p_type == type(dict())

def test_reprs():
    # Pattern matchers
    assert repr(pg.Some("a")) == "<Some pattern='a'>"
    assert repr(pg.Ignore("#")) == "<Ignore pattern='#'>"
    assert repr(pg.Not("#")) == "<Not pattern='#'>"
    assert repr(pg.Optional("#")) == "<Optional pattern='#'>"

    # Option matchers
    assert repr(pg.OneOf("abc", pg.Not("#"))) == "<OneOf options=('abc', <Not pattern='#'>)>"
    assert repr(pg.Many("abc", pg.Not("#"))) == "<Many options=('abc', <Not pattern='#'>)>"
    assert repr(pg.Words()) == "<Words letters='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,'>"

def test_add_match_to_result():
    def do_test(data):
        expected = ['useful_name', "flimmle", ['sub_item', "flammle"], "flapple"]
        result = ["useful_name"]
        pg._add_match_to_result(result, data)
        assert expected == result

    items = [
        ['', "flimmle", ['sub_item', "flammle"], "flapple"],
        ['<lambda>', "flimmle", ['sub_item', "flammle"], "flapple"],
        ['_ignore_me', "flimmle", ['sub_item', "flammle"], "flapple"]]

    for item in items:
        yield do_test, item

def test_get_current_indentation_initial_indent():
    indented_text =  pg.Indented(
        pg.Words(),
        initial_indent=pg.AllOf("*   "))

    data = "*   foo"
    expected = ("    ", "    foo")
    result = pg._get_current_indentation(data, indented_text)
    assert expected == result

def test_get_current_indentation():
    def do_test(data, expected_match, expected_rest):
        match, rest = pg._get_current_indentation(data)
        assert expected_match == match
        assert expected_rest == rest

    items = [
        (" foo", " ", " foo"),
        ("  foo", "  ", "  foo"),
        ("\tfoo", "\t", "\tfoo"),
        ("\t\tfoo", "\t\t", "\t\tfoo"),
        (" \tfoo", " ", " \tfoo"),
        ("\t foo", "\t", "\t foo")]

    for data, match, rest in items:
        yield do_test, data, match, rest

def test_get_indented_lines():
    data = [
        "\tOne",
        "\tTwo"
        ]

    expected = [
        "One",
        "Two"
        ]

    result = pg._get_indented_lines(data, "\t", list(data))
    assert expected == result
