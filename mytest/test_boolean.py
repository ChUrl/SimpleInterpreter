import py

from simpleparser import parse
from objmodel import W_NormalObject, W_Integer
from interpreter import Interpreter


def test_boolean_assignment():
    ast = parse("""
x = true
y = false
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    assert isinstance(w_model.getvalue("x"), W_Boolean)
    assert w_model.getvalue("x").istrue() is True
    assert isinstance(w_model.getvalue("y"), W_Boolean)
    assert w_model.getvalue("y").istrue() is False


def test_boolean_operations():
    ast = parse("""
x = true and(false)
y = true or(false)
z = not(true)
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    assert isinstance(w_model.getvalue("x"), W_Boolean)
    assert w_model.getvalue("x").istrue() is False
    assert isinstance(w_model.getvalue("y"), W_Boolean)
    assert w_model.getvalue("y").istrue() is True
    assert isinstance(w_model.getvalue("z"), W_Boolean)
    assert w_model.getvalue("z").istrue() is False


def test_boolean_result():
    ast = parse("""
x = 1 eq(2)
y = 1 leq(2)
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    assert isinstance(w_model.getvalue("x"), W_Boolean)
    assert w_model.getvalue("x").istrue() is False
    assert isinstance(w_model.getvalue("y"), W_Boolean)
    assert w_model.getvalue("y").istrue() is True


def test_boolean_conversion():
    ast = parse("""
x = 1 toboolean
y = true toint
z = false toint
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    assert isinstance(w_model.getvalue("x"), W_Boolean)
    assert w_model.getvalue("x").istrue() is True
    assert isinstance(w_model.getvalue("y"), W_Integer)
    assert w_model.getvalue("y").value == 1
    assert isinstance(w_model.getvalue("z"), W_Integer)
    assert w_model.getvalue("z").value == 0
