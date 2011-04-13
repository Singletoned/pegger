# -*- coding: utf-8 -*-

import utils

def test_deep_bool():
    assert not utils.deep_bool([''])
    assert not utils.deep_bool({'':''})
    assert not utils.deep_bool(('', ''))
    assert utils.deep_bool([[1]])
    assert utils.deep_bool(['', 'b'])
