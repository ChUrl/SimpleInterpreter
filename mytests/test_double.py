from simpleparser import parse
from objmodel import W_Integer
from interpreter import Interpreter


def test_double_assignment():
    ast = parse("""
x = 1.5
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    assert isinstance(w_model.getvalue("x"), W_Double)
    assert w_model.getvalue("x").value == 1.5


def test_double_operations():
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
