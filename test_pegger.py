# -*- coding: utf-8 -*-

import unittest

import py

import pegger as pg


def test_match_some():
    word_a = pg.Some('a')

    match, rest = word_a("a", "word_a")
    assert match == ['word_a', "a"]
    assert rest == ""

    match, rest = word_a("aab", "word_a")
    assert match == ['word_a', "aa"]
    assert rest == "b"

    with py.test.raises(pg.NoPatternFound):
        match, rest = word_a("ccc", "word_a")

def test_match_text():
    """Test that a text pattern removes the pattern from the beginning
    of the text and returns the rest"""

    letter_a = pg.Text("a")

    match, rest = letter_a("ab", "letter_a")
    assert match == ['letter_a', "a"]
    assert rest == "b"

    match, rest = letter_a("aabc", "letter_a")
    assert match == ['letter_a', "a"]
    assert rest == "abc"

    with py.test.raises(pg.NoPatternFound):
        match, rest = letter_a("ccc", "letter_a")

def test_match_words():
    """Test that Words matches letters and punctuation"""
    plain = pg.Words()

    match, rest = plain("some words", 'plain')
    assert match == ['plain', "some words"]
    assert rest == ""

    # Match with no name
    match, rest = plain("some words", '')
    assert match == ['', "some words"]
    assert rest == ""

    match, rest = plain("some words 123", 'plain')
    assert match == ['plain', "some words "]
    assert rest == "123"

    match, rest = plain("Some words, and punctuation.", 'plain')
    assert match == ['plain', "Some words, and punctuation."]
    assert rest == ""


def test_match_all_of():
    letter_a = pg.NamedPattern(
        'letter_a',
        "a")

    letter_b = pg.NamedPattern(
        'letter_b',
        "b")

    word_ab = pg.AllOf(letter_a, letter_b)

    match, rest = word_ab("ab", "word_ab")
    assert match == ['word_ab', ['letter_a', "a"], ['letter_b', "b"]]
    assert rest == ""

    word_abc = pg.AllOf(letter_a, pg.Words())

    expected = ['word_ab', ['letter_a', "a"], "bc"]
    match, rest = word_abc("abc", "word_ab")
    assert match == expected
    assert rest == ""

    match, rest = word_abc("abc!", "")
    assert match == ['', ['letter_a', "a"], "bc"]
    assert rest == "!"

    emphasis = pg.AllOf(
        pg.Ignore("*"),
        pg.Words(),
        pg.Ignore("*"))

    match, rest = emphasis("*abc*", "emphasis")
    assert match == ['emphasis', "abc"]

    with py.test.raises(pg.NoPatternFound):
        result = word_ab("cab", "word_ab")

    ignore_ab = pg.AllOf(
        pg.Ignore("a"),
        pg.Ignore("b"))

    match, rest = ignore_ab("ab", "ignore_ab")
    assert match == ['ignore_ab', ""]
    assert rest == ""

def test_match_ignore():
    ignore_a = pg.Ignore("a")

    match, rest = ignore_a("a", "ignore_a")
    assert match == []
    assert rest == ""

    ignore_a = pg.Ignore(
        pg.AllOf(pg.Optional("#"),
         "abc"))

    match, rest = ignore_a("#abc", "ignore_a")
    assert match == []
    assert rest == ""

    with py.test.raises(pg.NoPatternFound):
        match, rest = ignore_a("123", "ignore_a")

def test_match_one_of():
    asterix = pg.Ignore("*")

    emphasis = pg.AllOf(
        asterix,
        pg.Many(pg.Not("*")),
        asterix)

    phrase = pg.OneOf(
            pg.Words(),
            emphasis)

    expected = ['phrase', "b", "o", "l", "d"]
    match, rest = phrase("*bold*", "phrase")
    assert match == expected
    assert rest == ""

    with py.test.raises(pg.NoPatternFound):
        match, rest = phrase("123", "phrase")

    match, rest = phrase("text", "phrase")
    assert match == ['phrase', "text"]
    assert rest == ""

    # Test match with no name
    match, rest = phrase("text", "")
    assert match == ['', "text"]
    assert rest == ""

def test_match_one_of_empty():
    b1 = pg.Ignore("*")
    b2 = pg.Ignore("-")

    bullet = pg.OneOf(b1, b2)

    data = "*"
    expected = ['bullet', ""]
    match, rest = bullet(data, 'bullet')
    assert match == expected
    assert rest == ""

def test_match_many_simple():
    a = pg.NamedPattern(
        'a',
        "a")

    b = pg.NamedPattern(
        'b',
        "b")

    letters = pg.Many(a, b)

    expected = ['letters', ['a', "a"], ['b', "b"], ['a', "a"], ['b', "b"]]
    match, rest = letters("abab", "letters")
    assert match == expected
    assert rest == ""

    match, rest = letters("ababcc", "letters")
    assert match == ['letters', ['a', "a"], ['b', "b"], ['a', "a"], ['b', "b"]]
    assert rest == "cc"

    match, rest = letters("ababcc", "")
    assert match == ['', ['a', "a"], ['b', "b"], ['a', "a"], ['b', "b"]]
    assert rest == "cc"

    with py.test.raises(pg.NoPatternFound):
        match, rest = letters("cab", "letters")

def test_match_many_complex():
    emphasis = pg.NamedPattern(
        'emphasis',
        pg.AllOf(
            pg.Ignore("*"),
            pg.Words(),
            pg.Ignore("*")))

    words = pg.NamedPattern(
        'words',
        pg.Words())

    body = pg.Many(emphasis, words)

    expected = [
        'body',
        ['words', 'a phrase with '],
         ['emphasis', "bold words"],
         ['words', " in it"]]
    match, rest = body("a phrase with *bold words* in it", 'body')
    assert match == expected
    assert rest == ""

def test_match_many_empty():
    "Test that empty matches don't raise NoPatternFound"
    linebreaks = pg.Many(
        pg.OneOf(
            pg.Ignore(
                "\n")))

    data = "\n\n"
    expected = ['linebreaks', ""]
    match, rest = linebreaks(data, 'linebreaks')
    assert match == expected
    assert rest == ""

def test_match_many_specificty():
    letter_a = pg.NamedPattern(
        'letter_a',
        "a")

    letter_b = pg.NamedPattern(
        'letter_b',
        "b")

    other_letters = pg.NamedPattern(
        'other_letters',
        pg.Words())

    match_letters = pg.Many(
        letter_a,
        letter_b,
        other_letters)

    data = "abac"

    expected = [
        'match_letters',
        ['letter_a', "a"],
        ['letter_b', "b"],
        ['letter_a', "a"],
        ['other_letters', "c"]]

    match, rest = match_letters(data, 'match_letters')
    assert match == expected
    assert rest == ""

def test_match_join():
    three_times_a = pg.Join(
        pg.CountOf(
            3, "a"))

    data = "aaa"
    expected = ['three_times_a', "aaa"]
    match, rest = three_times_a(data, 'three_times_a')
    assert match == expected
    assert rest == ""

    not_d = pg.Join(
        pg.Many(
            pg.Not("d")))

    data = "abcd"
    expected = ['not_d', "abc"]
    match, rest = not_d(data, 'not_d')
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

    data = []
    expected = []
    result = pg.filter_match(data, recursive=True)
    assert result == expected

def test_match_count_of():
    three_dashes = pg.CountOf(3, "-")

    with py.test.raises(pg.NoPatternFound):
        match, rest = three_dashes("--", 'three_dashes')

    expected = [
        'three_dashes',
        "-", "-", "-"]

    match, rest = three_dashes("---", 'three_dashes')
    assert match == expected
    assert rest == ""

    expected = [
        'three_dashes',
        "-", "-", "-"]

    match, rest = three_dashes("----", 'three_dashes')
    assert match == expected
    assert rest == "-"

def test_match_insert():
    insert_a = pg.Insert("a")

    expected = ['insert_a', "a"]

    match, rest = insert_a("", 'insert_a')
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

    match, rest = joined_lines(data, 'joined_lines')
    assert match == expected
    assert rest == ""

def test_match_not():
    not_a = pg.Not("a")

    match, rest = not_a("b", 'not_a')
    assert match == ['not_a', "b"]
    assert rest == ""

    match, rest = not_a("ba", 'not_a')
    assert match == ['not_a', "b"]
    assert rest == "a"

    with py.test.raises(pg.NoPatternFound):
        match, rest = not_a("abc", 'not_a')

    match, rest = not_a("bcd", 'not_a')
    assert match == ['not_a', "b"]
    assert rest == "cd"

    with py.test.raises(pg.NoPatternFound):
        match, rest = not_a("", 'not_a')

    not_a_or_b = pg.Not(pg.OneOf("a", "b"))

    match, rest = not_a_or_b("cca", 'not_a_or_b')
    assert match == ['not_a_or_b', "c"]
    assert rest == "ca"

    with py.test.raises(pg.NoPatternFound):
        match, rest = not_a_or_b("abc", 'not_a_or_b')

    with py.test.raises(pg.NoPatternFound):
        match, rest = not_a_or_b("bbc", 'not_a_or_b')

def test_match_optional():
    optional_a = pg.Optional("a")

    match, rest = optional_a("abc", 'optional_a')
    assert match == ['', "a"]
    assert rest == "bc"

    match, rest = optional_a("bc", 'optional_a')
    assert match == []
    assert rest == "bc"

    letter_a = pg.NamedPattern(
        'letter_a',
        "a")

    optional_a = pg.Optional(letter_a)
    match, rest = optional_a("abc", 'optional_a')
    assert match == ['letter_a', "a"]
    assert rest == "bc"

    optional_ignore = pg.Optional(pg.Ignore("a"))

    match, rest = optional_ignore("abc", 'optional_ignore')
    assert match == []
    assert rest == "bc"

def test_match_eof():
    eof = pg.EOF()
    match, rest = eof("", 'eof')
    assert match == ['eof', '']

    text_then_eof = pg.AllOf(
        "a",
        pg.EOF())
    match, rest = text_then_eof("a", 'text_then_eof')
    assert match == ['text_then_eof', 'a', '']


class TestMatchIndented(unittest.TestCase):
    """Unittests for match_indented"""

    def test_without_optional(self):
        """Test that without optional, no match is made"""
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
            match, rest = indented_bullets(data, 'indented_bullets')

    def test_with_optional(self):
        """Test that optional allows you to match without an indent"""
        list_item = pg.NamedPattern(
            'list_item',
            pg.AllOf(
                pg.Ignore("* "),
                pg.Words()))

        indented_bullets = pg.Indented(
            pg.Many(list_item),
            optional=True)

        data = """* A bullet"""

        expected = [
            'indented_bullets',
            ['list_item', "A bullet"]]

        match, rest = indented_bullets(data, 'indented_bullets')
        assert match == expected
        assert rest == ""

    def test_indented_with_named_subpattern(self):
        paragraph = pg.NamedPattern(
            'paragraph',
            pg.Words())

        indented_text = pg.Indented(paragraph)

        data_with_spaces = """  Some text"""
        data_with_tabs = """\tSome text"""

        expected = [
            'indented_text',
            ['paragraph', "Some text"]]

        for data in [data_with_spaces, data_with_tabs]:
            match, rest = indented_text(data, 'indented_text')
            assert match == expected
            assert rest == ""

    def test_indented_with_anonymous_subpattern(self):
        paragraph = (
            pg.Words())

        indented_text = pg.Indented(paragraph)

        data = "  Some text"

        expected = [
            'indented_text',
            "Some text"]

        match, rest = indented_text(data, 'indented_text')
        assert match == expected
        assert rest == ""

    def test_indented_with_anonymous_pattern_and_subpattern(self):
        paragraph = (
            pg.Words())

        indented_text = pg.Indented(paragraph)

        data = "  Some text"

        expected = [None, "Some text"]

        match, rest = indented_text(data, None)
        assert match == expected
        assert rest == ""

    def test_retaining_linebreaks(self):
        paragraph = (
            pg.Words())

        indented_text = pg.Indented(paragraph)

        data = "  Some text\n"

        expected = ['indented_text', "Some text"]

        match, rest = indented_text(data, 'indented_text')
        assert match == expected
        assert rest == "\n"

    def test_reindenting_indented_rest(self):
        paragraph = (
            pg.Words())

        indented_text = pg.Indented(paragraph)

        data = "  Some text\n  Unmatched text\n  More unmatched text"

        expected = ['indented_text', "Some text"]
        expected_rest = "\n  Unmatched text\n  More unmatched text"

        match, rest = indented_text(data, 'indented_text')
        assert match == expected
        assert rest == expected_rest

    def test_with_indent_chars(self):
        "Test that Indented can match with indents other than whitespace"
        lines = pg.Many(
            pg.OneOf(
                pg.Words(),
                pg.Text("\n")))
        indented_text = pg.Indented(
            lines,
            indent_pattern="> ")

        data = """
> Some text
> indented with
> non whitespace
""".strip()

        expected = ['indented_text',
                    "Some text",
                    "\n",
                    "indented with",
                    "\n",
                    "non whitespace"]

        match, rest = indented_text(data, 'indented_text')
        assert match == expected
        assert rest == ""

def test_match_indented_nested_bullets():
    bullet = pg.NamedPattern(
        'bullet',
        pg.AllOf(
            pg.Ignore(
                pg.Optional(
                    pg.Many("\n"))),
            pg.Ignore("* "),
            pg.Words()))

    def indented_bullets():
        return pg.Indented(
            pg.AllOf(
                bullet,
                pg.Optional(
                    indented_bullets)),
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

    match, rest = indented_bullets()(data, 'indented_bullets')
    assert match == expected
    assert rest == "\n"

def test_indented_bullet():
    paragraph = pg.NamedPattern(
        'paragraph',
        pg.AllOf(
            pg.Ignore(pg.Optional("\n")),
            pg.Words()))

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

    match, rest = indented_paragraphs(data, "indented_paragraphs")
    assert match == expected

def test_match_escaped():
    html_text = pg.NamedPattern(
        'html_text',
        pg.Many(
            pg.Words(
                pg.Words.letters + "</>")))

    escaped_text = pg.Escaped(html_text)

    data = """<p>Some text</p>"""

    expected = [
        'escaped_text',
        ['html_text', "&lt;p&gt;Some text&lt;/p&gt;"]]

    match, rest = escaped_text(data, 'escaped_text')
    assert match == expected
    assert rest == ""

def test_match_lookahead():
    foo_pattern = pg.Lookahead("foo")

    data = """
bar
baz
foo
""".strip()

    expected = [
        'foo_pattern',
        "foo"]

    match, rest = foo_pattern(data, 'foo_pattern')
    assert match == expected
    assert rest == "bar\nbaz\n"

def test_parse_string_a():
    letter_a = pg.NamedPattern("letter_a", "a")

    result = pg.parse_string("a", letter_a)
    assert result == ['letter_a', "a"]

    result = pg.parse_string("ab", letter_a)
    assert result == ['letter_a', "a"]

    with py.test.raises(pg.NoPatternFound):
        result = pg.parse_string("c", letter_a)

def test_parse_string_b():
    letter_b = pg.NamedPattern("letter_b", "b")

    result = pg.parse_string("b", letter_b)
    assert result == ['letter_b', "b"]

    with py.test.raises(pg.NoPatternFound):
        result = pg.parse_string("c", letter_b)

def test_parse_string_ab():
    letter_a = pg.NamedPattern("letter_a", "a")
    letter_b = pg.NamedPattern("letter_b", "b")
    word_ab = pg.NamedPattern(
        'word_ab',
        pg.AllOf(letter_a, letter_b))

    expected = ['word_ab',
                ['letter_a', "a"],
                ['letter_b', "b"]]

    result = pg.parse_string("ab", word_ab)
    assert result == expected

    with py.test.raises(pg.NoPatternFound):
        result = pg.parse_string("cab", word_ab)

def test_parse_string_some_a():
    word_a = pg.NamedPattern(
        'word_a',
        pg.Some('a'))

    result = pg.parse_string("aa", word_a)
    assert result == ['word_a', "aa"]

    result = pg.parse_string("aaa", word_a)
    assert result == ['word_a', "aaa"]

    with py.test.raises(pg.NoPatternFound):
        result = pg.parse_string("caa", word_a)

def test_parse_string_some_aab():
    word_a = pg.NamedPattern("word_a", pg.Some('a'))
    letter_b = pg.NamedPattern("letter_b", "b")
    word_aab = pg.NamedPattern(
        'word_aab',
        pg.AllOf(word_a, letter_b))

    expected = ['word_aab',
                ['word_a', "aa"],
                ['letter_b', "b"]]

    result = pg.parse_string("aab", word_aab)
    assert result == expected

    with py.test.raises(pg.NoPatternFound):
        result = pg.parse_string("caab", word_aab)

def test_parse_words():
    body = pg.NamedPattern(
        'body',
        pg.Words())

    result = pg.parse_string("The confused dog jumped over the fox", body)
    assert result == ['body', "The confused dog jumped over the fox"]

def test_parse_ignore():
    emphasis = pg.NamedPattern(
        'emphasis',
        pg.AllOf(
            pg.Ignore("*"),
            pg.Words(),
            pg.Ignore("*")))

    result = pg.parse_string("*bold words*", emphasis)
    assert result == ['emphasis', "bold words"]

def test_parse_one_of():
    emphasis = pg.NamedPattern(
        'emphasis',
        pg.AllOf(
            pg.Ignore("*"),
            pg.Words(),
            pg.Ignore("*")))

    words = pg.NamedPattern(
        'words',
        pg.Words())

    phrase = pg.NamedPattern(
        'phrase',
        pg.OneOf(
            words,
            emphasis))

    expected = ['phrase', ['emphasis', "bold words"]]
    result = pg.parse_string("*bold words*", phrase)
    assert result == expected

    expected = ['phrase', ['words', "normal words"]]
    result = pg.parse_string("normal words", phrase)
    assert result == expected

def test_parse_many():
    emphasis = pg.NamedPattern(
        'emphasis',
        pg.AllOf(
            pg.Ignore("*"),
            pg.Words(),
            pg.Ignore("*")))

    words = pg.NamedPattern(
        'words',
        pg.Words())

    phrase = pg.NamedPattern(
        'phrase',
        pg.OneOf(
            words,
            emphasis))

    body = pg.NamedPattern(
        'body',
        pg.Many(phrase))

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
    not_a = pg.NamedPattern(
        'not_a',
        pg.Not("a"))

    result = pg.parse_string("bc", not_a)
    assert result == ['not_a', 'b']

    with py.test.raises(pg.NoPatternFound):
        result = pg.parse_string("a", not_a)

def test_optional():
    optional_a = pg.NamedPattern(
        'optional_a',
        pg.Optional("a"))

    result = pg.parse_string("a", optional_a)
    expected = ['', "a"]
    assert expected == result

    letters = pg.NamedPattern(
        'letters',
        pg.Words())

    body = pg.NamedPattern(
        'body',
        pg.AllOf(optional_a, letters))

    result = pg.parse_string("abc", body)
    expected = [
        'body',
        "a",
        ['letters', "bc"]]
    assert expected == result

def test_indented():
    list_item = pg.NamedPattern(
        'list_item',
        pg.AllOf(
            pg.Ignore(
                pg.Optional(
                    pg.Many("\n"))),
            pg.Ignore("* "),
            pg.Words()))

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
    html_text = pg.NamedPattern(
        'html_text',
        pg.Many(
            pg.Words(
                pg.Words.letters+"</>")))

    escaped_text = pg.NamedPattern(
        'escaped_text',
        pg.Escaped(html_text))

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

    escaped_text = pg.NamedPattern(
        'escaped_text',
        pg.Escaped(html_text))

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
    assert repr(pg.Ignore("#")) == "<Ignore pattern=<Text pattern='#'>>"
    assert repr(pg.Not("#")) == "<Not pattern=<Text pattern='#'>>"
    assert repr(pg.Optional("#")) == "<Optional pattern=<Text pattern='#'>>"

    # Option matchers
    assert repr(pg.OneOf("abc", pg.Not("#"))) == "<OneOf options=(<Text pattern='abc'>, <Not pattern=<Text pattern='#'>>)>"
    assert repr(pg.Many("abc", pg.Not("#"))) == "<Many options=(<Text pattern='abc'>, <Not pattern=<Text pattern='#'>>)>"
    assert repr(pg.Words()) == "<Words letters='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,'>"

def test_add_match_to_result():
    def do_test(data):
        expected = ['useful_name', "flimmle", ['sub_item', "flammle"], "flapple"]
        result = ["useful_name"]
        pg.pegger._add_match_to_result(result, data)
        assert expected == result

    items = [
        ['', "flimmle", ['sub_item', "flammle"], "flapple"],
        ['<lambda>', "flimmle", ['sub_item', "flammle"], "flapple"],
        ['_ignore_me', "flimmle", ['sub_item', "flammle"], "flapple"]]

    for item in items:
        yield do_test, item

def test_get_current_indentation_initial_indent():
    indented_text = pg.Indented(
        pg.Words(),
        initial_indent=pg.AllOf("*   "))

    data = "*   foo"
    expected = ("    ", "    foo")
    result = pg.pegger._get_current_indentation(data, indented_text)
    assert expected == result

def test_get_current_indentation_initial_indent_with_tabs():
    indented_text = pg.Indented(
        pg.Words(),
        initial_indent=pg.AllOf(pg.Ignore("*"), "\t"))

    data = "*\tfoo"
    expected = ("\t", "\tfoo")
    result = pg.pegger._get_current_indentation(data, indented_text)
    assert expected == result

def test_get_current_indentation():
    def do_test(data, expected_match, expected_rest):
        match, rest = pg.pegger._get_current_indentation(data)
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
    def do_test(indent, data, expected):
        result = pg.pegger._get_indented_lines(data, indent)
        assert expected == result

    items = [
        ["\t", ["\tOne", "\tTwo"], ["One", "Two"]],
        [" ", ["\tOne", "\tTwo"], []],
        ["\t", [" One", " Two"], []],
        [" ", [" One", " Two"], ["One", "Two"]],
        ["  ", ["   One", "   Two"], [" One", " Two"]],
        ["\t", ["\t\tOne", "\t\tTwo"], ["\tOne", "\tTwo"]],
        ["  ", ["  One", "", "  Two"], ["One", "", "Two"]],
        ["\t", ["\tOne", "", "\tTwo"], ["One", "", "Two"]],
        ["  ", ["  One", "", "", "  Two"], ["One"]],
        ["\t", ["\tOne", "", "", "\tTwo"], ["One"]],
        ]

    for indent, data, expected in items:
        yield do_test, indent, data, expected
