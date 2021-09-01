from rply import Token

from interpreter import Interpreter
from simplelexer import lex
from simpleparser import parse


def sugar_test_helper(expr):
    ast = parse("x = " + expr)
    interpreter = Interpreter()
    w_module = interpreter.make_module()
    interpreter.eval(ast, w_module)

    return w_module.getvalue("x").value


def test_lexing():
    token = lex("+ - * / ++ %")

    assert Token("Plus", "+") == token[0]
    assert Token("Minus", "-") == token[1]
    assert Token("Multiply", "*") == token[2]
    assert Token("Divide", "/") == token[3]
    assert Token("Increment", "++") == token[4]
    assert Token("Modulo", "%") == token[5]


def test_parsing():
    assert parse("1 + 2") == parse("1 add(2)")
    assert parse("1 + 2 + 3") == parse("1 add(2) add(3)")
    assert parse("1 + 2 * 3") == parse("1 add(2 mul(3))")
    assert parse("1 - 2 - 3") == parse("1 sub(2) sub(3)")
    assert parse("1 + 2 % 3 / 4 - 5 * 6 + 7++") == parse("1 add(2 mod(3) div(4)) sub(5 mul(6)) add(7 inc)")


def test_parsing_parenthesis():
    assert parse("(1 + 2)") == parse("1 add(2)")
    assert parse("1 * (2 + 3)") == parse("1 mul(2 add(3))")


def test_sugar_builtins():
    assert sugar_test_helper("2 add(5)") == 7
    assert sugar_test_helper("2 mul(5)") == 10
    assert sugar_test_helper("2 div(5)") == 0
    assert sugar_test_helper("10 div(5)") == 2
    assert sugar_test_helper("10 div(3)") == 3
    assert sugar_test_helper("5 mod(3)") == 2
    assert sugar_test_helper("4 mod(2)") == 0
    assert sugar_test_helper("2 inc") == 3


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
    assert sugar_test_helper("1 ++ + 1") == 3
    assert sugar_test_helper("2 * 2 ++") == 6

    ast = parse("""
i = 1
i++
x = i
""")
    interpreter = Interpreter()
    w_module = interpreter.make_module()
    interpreter.eval(ast, w_module)

    assert w_module.getvalue("x").value == 2


def test_inplace_arithmetic():
    ast = parse("""
w = 5
x = 5
y = 5
z = 5
w += 1
x -= 2
y *= 5
z /= 2
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    assert w_model.getvalue("w").value == 6
    assert w_model.getvalue("x").value == 3
    assert w_model.getvalue("y").value == 25
    assert w_model.getvalue("z").value == 2


def test_comparisons():
    ast = parse("""
u = 5 < 3
v = 5 <= 5
w = 5 > 3
x = 5 >= 3
y = 5 == 6
z = 5 != 6
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    assert w_model.getvalue("u").istrue() is False
    assert w_model.getvalue("v").istrue() is True
    assert w_model.getvalue("w").istrue() is True
    assert w_model.getvalue("x").istrue() is True
    assert w_model.getvalue("y").istrue() is False
    assert w_model.getvalue("z").istrue() is True


def test_logical():
    ast = parse("""
x = true && false
y = true || false
z = !true
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    assert w_model.getvalue("x").istrue() is False
    assert w_model.getvalue("y").istrue() is True
    assert w_model.getvalue("z").istrue() is False


def test_mixed_precedence():
    assert sugar_test_helper("2 * 3 / 2") == 3
    assert sugar_test_helper("1 + 2 + 3 - 5") == 1
    assert sugar_test_helper("10 - 2 * 5") == 0
    assert sugar_test_helper("1 + 2 * 2 * 3 - 3 * 4") == 1


def test_parenthesis():
    assert sugar_test_helper("2 * (2 + 3)") == 10
    assert sugar_test_helper("(2 + 5)") == 7
    assert sugar_test_helper("(3 + 3) % 2") == 0
    assert sugar_test_helper("(2 * 2) ++") == 5
