import py

from simpleparser import parse
from objmodel import W_NormalObject, W_Integer
from interpreter import Interpreter


def test_string_assignment():
    ast = parse("""
x = "Hallo"
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    assert isinstance(w_model.getvalue("x"), W_String)
    assert w_model.getvalue("x").value == "Hallo"


def test_string_operations():
    ast = parse("""
x = "Hallo" add("ollaH")
y = "Hallo" rev
z = "Hallo" len
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    assert isinstance(w_model.getvalue("x"), W_String)
    assert w_model.getvalue("x").value == "HalloollaH"
    assert isinstance(w_model.getvalue("y"), W_String)
    assert w_model.getvalue("y").value == "ollaH"
    assert isinstance(w_model.getvalue("z"), W_Integer)
    assert w_model.getvalue("z").value == 5
