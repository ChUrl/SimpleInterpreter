from rply import Token

from simpleast import Program, ExprStatement, ImplicitSelf, Assignment, DoubleLiteral
from simplelexer import lex
from simpleparser import parse
from objmodel import W_Integer, W_Double
from interpreter import Interpreter


def test_basic_double_lexing():
    assert lex("0.1")[0] == Token("Double", "0.1")
    assert lex(".1")[0] == Token("Double", ".1")
    assert lex("1.")[0] == Token("Double", "1.")
    assert lex("-5.5")[0] == Token("Double", "-5.5")
    assert lex("-.5")[0] == Token("Double", "-.5")
    assert lex("x = 0.0005")[:3] == [Token("Name", "x"), Token("Assign", "="), Token("Double", "0.0005")]


def test_basic_double_parsing():
    assert parse("1.0") == Program([ExprStatement(DoubleLiteral("1.0"))])
    assert parse("x = -.1") == Program([Assignment(ImplicitSelf(), "x", DoubleLiteral("-0.1"))])


def test_double_assignment():
    ast = parse("""
x = 1.5
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    assert isinstance(w_model.getvalue("x"), W_Double)
    assert w_model.getvalue("x").value == 1.5


def test_double_addition_subtraction():
    ast = parse("""
x = 2.5 sub(2.4)
y = 2.5 add(2.4)
z = 3 sub(2.5)
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    assert isinstance(w_model.getvalue("x"), W_Double)
    assert w_model.getvalue("x").value == (2.5 - 2.4)
    assert isinstance(w_model.getvalue("y"), W_Double)
    assert w_model.getvalue("y").value == (2.5 + 2.4)
    assert isinstance(w_model.getvalue("z"), W_Integer)
    assert w_model.getvalue("z").value == 0


def test_double_division():
    ast = parse("""
x = 3 div(2)
y = 3 div(2.0)
z = 3.0 div(2.0)
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    assert isinstance(w_model.getvalue("x"), W_Integer)
    assert w_model.getvalue("x").value == 1
    assert isinstance(w_model.getvalue("y"), W_Integer)
    assert w_model.getvalue("y").value == 1
    assert isinstance(w_model.getvalue("z"), W_Double)
    assert w_model.getvalue("z").value == 1.5


def test_double_multiplication():
    ast = parse("""
x = 3.3 mul(3.0)
y = 3.3 mul(3)
z = 3 mul(3.3)
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    assert isinstance(w_model.getvalue("x"), W_Double)
    assert w_model.getvalue("x").value == (3.3 * 3.0)
    assert isinstance(w_model.getvalue("y"), W_Double)
    assert w_model.getvalue("y").value == (3.3 * 3)
    assert isinstance(w_model.getvalue("z"), W_Integer)
    assert w_model.getvalue("z").value == 9


def test_double_conversion():
    ast = parse("""
x = 1.5 toint
y = 2.0 toint
z = 3 todouble
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    assert isinstance(w_model.getvalue("x"), W_Integer)
    assert w_model.getvalue("x").value == 1
    assert isinstance(w_model.getvalue("y"), W_Integer)
    assert w_model.getvalue("y").value == 2
    assert isinstance(w_model.getvalue("z"), W_Double)
    assert w_model.getvalue("z").value == 3.0
