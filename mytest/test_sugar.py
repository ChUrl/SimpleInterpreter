import py

from simpleparser import parse
from objmodel import W_NormalObject
from interpreter import Interpreter


def sugar_test_helper(expr):
    ast = parse("x = " + expr)
    interpreter = Interpreter()
    w_module = interpreter.make_module()
    interpreter.eval(ast, w_module)

    return w_module.getvalue("x").value


def test_plus():
    assert sugar_test_helper("1 + 1 + 1") == 3
    assert sugar_test_helper("1 + 1") == 2


def test_minus():
    assert sugar_test_helper("2 - 1") == 1
    assert sugar_test_helper("3 - 1 - 1") == 1


def test_mult():
    assert sugar_test_helper("2 * 5") == 10
    assert sugar_test_helper("2 * 3 * 4") == 24


def test_div():
    assert sugar_test_helper("10 / 2") == 5
    assert sugar_test_helper("24 / 3 / 2") == 4


def test_mod():
    assert sugar_test_helper("11 % 2") == 1


def test_inc():
    assert sugar_test_helper("1 ++") == 2


def test_mixed_precedence():
    assert sugar_test_helper("2 * 3 / 2") == 3
    assert sugar_test_helper("1 + 2 + 3 - 5") == 1
    assert sugar_test_helper("10 - 2 * 5") == 0
    assert sugar_test_helper("1 + 2 * 2 * 3 - 3 * 4") == 1
