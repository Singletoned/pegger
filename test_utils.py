# -*- coding: utf-8 -*-

import itertools

import utils

def test_deep_bool():
    assert not utils.deep_bool([''])
    assert not utils.deep_bool({'':''})
    assert not utils.deep_bool(('', ''))
    assert utils.deep_bool([[1]])
    assert utils.deep_bool(['', 'b'])

def test_memoise():
    counter = itertools.count()

    @utils.memoise
    def my_func(foo, bar):
        return repr((foo, bar, counter.next()))

    assert my_func(1, 2) == "(1, 2, 0)"
    assert my_func(1, 2) == "(1, 2, 0)"
    assert my_func(1, bar=2) == "(1, 2, 1)"
    assert my_func(1, bar=2) == "(1, 2, 1)"
    assert my_func(2, bar=3) == "(2, 3, 2)"
    assert my_func(2, bar=3) == "(2, 3, 2)"
