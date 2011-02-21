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

    match, rest = pg.match_words("some words 123", plain, 'plain')
    assert match == ['plain', "some words "]
    assert rest == "123"

    match, rest = pg.match_words("Some words, and punctuation.", plain, 'plain')
    assert match == ['plain', "Some words, and punctuation."]
    assert rest == ""


def test_match_tuple():
    def letter_a():
        return "a"

    def letter_b():
        return "b"

    word_ab = (letter_a, letter_b)

    match, rest = pg.match_tuple("ab", word_ab, "word_ab")
    assert match == ['word_ab', ['letter_a', "a"], ['letter_b', "b"]]
    assert rest == ""

    word_abc = (letter_a, pg.Words())

    expected = ['word_ab', ['letter_a', "a"], "bc"]
    match, rest = pg.match_tuple("abc", word_abc, "word_ab")
    assert match == expected
    assert rest == ""

    match, rest = pg.match_tuple("abc!", word_abc, "")
    assert match == ['', ['letter_a', "a"], "bc"]
    assert rest == "!"

    emphasis = (
        lambda: pg.Ignore("*"),
        lambda: pg.Words(),
        lambda: pg.Ignore("*"))

    match, rest = pg.match_tuple("*abc*", emphasis, "emphasis")
    assert match == ['emphasis', "abc"]

    with py.test.raises(pg.NoPatternFound):
        result = pg.match_tuple("cab", word_ab, "word_ab")

def test_match_ignore():
    ignore_a = pg.Ignore("a")

    match, rest = pg.match_ignore("a", ignore_a, "ignore_a")
    assert match == []
    assert rest == ""

    ignore_a = pg.Ignore(
        (pg.Optional("#"),
         "abc"))

    match, rest = pg.match_ignore("#abc", ignore_a, "ignore_a")
    assert match == []
    assert rest == ""

    with py.test.raises(pg.NoPatternFound):
        match, rest = pg.match_ignore("123", ignore_a, "ignore_a")

def test_match_one_of():
    def emphasis():
        return (
            lambda: pg.Ignore("*"),
            lambda: pg.Words(),
            lambda: pg.Ignore("*"))

    def words():
        return pg.Words()

    phrase = pg.OneOf(
            words,
            emphasis)

    match, rest = pg.match_one_of("*bold*", phrase, "phrase")
    assert match == ['emphasis', "bold"]
    assert rest == ""

    with py.test.raises(pg.NoPatternFound):
        match, rest = pg.match_one_of("123", phrase, "phrase")

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
        return (
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

    match, rest = pg.match_tuple(data, list_item(), 'list_item')
    assert match == expected
    assert rest == ""

    data = """
  * A bullet"""

    expected = [
        'indented_bullets',
        ['list_item', "A bullet"]]

    match, rest = pg.match_indented(data, indented_bullets, 'indented_bullets')
    assert match == expected
    assert rest == "\n"

    def paragraph():
        return (
            pg.Ignore("\n"),
            pg.Words())

    indented_text = pg.Indented(paragraph)

    data = """
    Some text"""

    expected = [
        'indented_text',
        ['paragraph', "Some text"]]

    match, rest = pg.match_indented(data, indented_text, 'indented_text')
    assert match == expected
    assert rest == "\n"

    # Check indented with unnamed subpattern

    paragraph = (
        pg.Ignore("\n"),
        pg.Words())

    indented_text = pg.Indented(paragraph)

    expected = [
        'indented_text',
        "Some text"]

    match, rest = pg.match_indented(data, indented_text, 'indented_text')
    assert match == expected
    assert rest == "\n"

    # Check indented with unnamed pattern and unnamed subpattern

    match, rest = pg.match_indented(data, indented_text, 'indented_text')
    assert match == expected
    assert rest == "\n"

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
        return (letter_a, letter_b)

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
        return (word_a, letter_b)

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

def test_parse_many():
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

    def body():
        return pg.Many(phrase)

    expected = ['body',
                ['words', 'a phrase with '],
                ['emphasis', "bold words"],
                ['words', " in it"]]

    result = pg.parse_string("a phrase with *bold words* in it", body)
    assert result == expected

    with py.test.raises(pg.NoPatternFound):
        result = pg.parse_string("123", body)

def test_not():
    def not_a():
        return pg.Not("a")

    result = pg.parse_string("bc", not_a)
    assert result == ['not_a', 'bc']

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
        return (optional_a, letters)

    result = pg.parse_string("abc", body)
    expected = [
        'body',
        "a",
        ['letters', "bc"]]
    assert expected == result

def test_indented():
    def list_item():
        return (
            pg.Ignore("\n* "),
            pg.Words())

    def nested_list():
        return (
            list_item,
            pg.Optional(
                pg.Many(
                    list_item,
                    pg.Indented(
                        nested_list))))

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

def test_make_block():
    data = ['list_item', "blah, blah"]
    expected = [
        "<li>",
        "  blah, blah",
        "</li>"]
    result = pg.make_block(data[0], data[1:])
    assert expected == result

    data = [
        'ordered_list',
        ['list_item', "A bullet"],
        ['list_item', "Another bullet"]]
    expected = [
        "<ol>",
        "  <li>",
        "    A bullet",
        "  </li>",
        "  <li>",
        "    Another bullet",
        "  </li>",
        "</ol>"]
    result = pg.make_block(data[0], data[1:])
    assert expected == result

def test_make_span():
    data = ['emphasis', "some bold"]
    expected = ["<strong>some bold</strong>"]
    result = pg.make_span(data[0], data[1:])
    assert expected == result

    data = [
        'plain',
        "A paragraph with ",
        ['emphasis', "some bold"],
        " and ",
        ['code', "code"],
        " in it"]
    expected = ["A paragraph with <strong>some bold</strong> and <code>code</code> in it"]
    result = pg.make_span(data[0], data[1:])
    assert expected == result

def test_do_render():
    data = [
        'list_item',
        ['emphasis',
         "some bold"]]
    expected = [
        "<li>",
        "  <strong>some bold</strong>",
        "</li>"]
    result = pg.do_render(data)
    assert expected == result

def test_htmlise():
    data = ['list_item', "A bullet"]
    expected = """
<li>
  A bullet
</li>""".strip()
    result = pg.htmlise(data)
    assert expected == result

    data = [
        'ordered_list',
        ['list_item', "A bullet"]]
    expected = """
<ol>
  <li>
    A bullet
  </li>
</ol>""".strip()
    result = pg.htmlise(data)
    assert expected == result

    data = [
        'list_item',
        ['plain',
         "A bullet with some ",
         ['emphasis',
          "bold"],
         " in it"]]
    expected = """
<li>
  A bullet with some <strong>bold</strong> in it
</li>""".strip()
    result = pg.htmlise(data)
    assert expected == result


def test_htmlise_2():
    def list_item():
        return (
            pg.Ignore("\n* "),
            pg.Many(
                pg.Words(),
                code,
                emphasis))

    def code():
        return (
            pg.Ignore("`"),
            pg.Not("`"),
            pg.Ignore("`"))

    def emphasis():
        return (
            pg.Ignore('*'),
            pg.Words(),
            pg.Ignore('*'))

    def nested_list():
        return (
            list_item,
            pg.Optional(
                pg.Many(
                    list_item,
                    pg.Indented(
                        nested_list))))

    data = """
* A numbered bullet
  * A bullet in a sublist
  * A bullet with *bold* in a sublist
* A bullet with `code` in the first list
"""

    expected = [
        'nested_list',
       ['list_item',
        "A numbered bullet"],
        ['nested_list',
         ['list_item',
          "A bullet in a sublist"],
         ['list_item',
          "A bullet with ",
          ['emphasis', "bold"],
          " in a sublist"]],
        ['list_item',
         "A bullet with ",
         ['code', "code"],
         " in the first list"]]

    result = pg.parse_string(data, nested_list)
    assert expected == result

    expected_html = """
<ol>
  <li>
    A numbered bullet
  </li>
  <ol>
    <li>
      A bullet in a sublist
    </li>
    <li>
      A bullet with <strong>bold</strong> in a sublist
    </li>
  </ol>
  <li>
    A bullet with <code>code</code> in the first list
  </li>
</ol>""".strip()

    result = pg.htmlise(expected)
    assert result == expected_html


def test_htmlise_link():
    def link():
        return (link_text, link_url)

    def link_text():
        return (
            pg.Ignore("["),
            pg.Words(),
            pg.Ignore("]"))

    def link_url():
        return (
            pg.Ignore("("),
            pg.Not(")"),
            pg.Ignore(")"))

    data = "[a link to Google](http://www.google.com)"
    expected = [
        'link',
        ['link_text', "a link to Google"],
        ['link_url',
         "http://www.google.com"]]
    result = pg.parse_string(data, link)
    assert expected == result

    expected_html = ['''
    <a href="http://www.google.com">a link to Google</a>
    '''.strip()]
    result = pg.make_anchor(expected[0], expected[1:])
    assert expected_html == result

    expected_html = '''
    <a href="http://www.google.com">a link to Google</a>
    '''.strip()
    result = pg.htmlise(expected)
    assert expected_html == result
