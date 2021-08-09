import py

from simpleparser import parse
from objmodel import W_NormalObject, W_Integer
from interpreter import Interpreter


def test_reassignment_gc():
    ast = parse("""
x = 2
y = 3
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    x = w_model.getvalue("x")
    y = w_model.getvalue("y")
    assert x in interpreter.space.realm  # Wo alle Objekte leben
    assert y in interpreter.space.realm

    ast = parse("""
x = y
""")
    interpreter.eval(ast, w_model)
    interpreter.space.gc()
    assert x not in interpreter.space.realm
    assert y in interpreter.space.realm

    ast = parse("""
x = 0
""")
    interpreter.eval(ast, w_model)
    interpreter.space.gc()
    assert x not in interpreter.space.realm
    assert y not in interpreter.space.realm


def test_chain_gc():
    ast = parse("""
x = 1
y = x
z = y
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    x = w_model.getvalue("x")
    assert x in interpreter.space.realm

    ast = parse("""
x = 0
""")
    interpreter.eval(ast, w_model)
    interpreter.space.gc()
    assert x in interpreter.space.realm

    ast = parse("""
y = x
z = y
""")
    interpreter.eval(ast, w_model)
    interpreter.space.gc()
    assert x not in interpreter.space.realm


def test_while_gc():
    ast = parse("""
x = 10
while x:
    x = x $int_add(-1)
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    count = len(interpreter.space.realm)
    interpreter.space.gc()

    assert count - len(interpreter.space.realm) == 10


def test_object_gc():
    ast = parse("""
object x:
    a = 1
    b = 2
    c = 3
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    a = w_model.getvalue("x").getvalue("a")
    b = w_model.getvalue("x").getvalue("b")
    c = w_model.getvalue("x").getvalue("c")
    assert a in interpreter.space.realm
    assert b in interpreter.space.realm
    assert c in interpreter.space.realm

    ast = parse("""
x = 0
""")
    interpreter.eval(ast, w_model)
    interpreter.space.gc()
    assert a not in interpreter.space.realm
    assert b not in interpreter.space.realm
    assert c not in interpreter.space.realm
