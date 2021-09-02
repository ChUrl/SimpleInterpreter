from simpleparser import parse
from interpreter import Interpreter


def test_reassignment_gc():
    ast = parse("""
x = 2
y = 3
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)
    interpreter.space.gc(w_model)

    x = w_model.getvalue("x")
    y = w_model.getvalue("y")
    assert x in interpreter.space.objects
    assert y in interpreter.space.objects

    ast = parse("""
x = y
""")
    interpreter.eval(ast, w_model)
    interpreter.space.gc(w_model)
    assert x not in interpreter.space.objects
    assert y in interpreter.space.objects

    ast = parse("""
x = 0
y = 0
""")
    interpreter.eval(ast, w_model)
    interpreter.space.gc(w_model)
    assert x not in interpreter.space.objects
    assert y not in interpreter.space.objects


def test_chain_gc():
    ast = parse("""
x = 1
y = x
z = y
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)
    interpreter.space.gc(w_model)

    x = w_model.getvalue("x")
    assert x in interpreter.space.objects

    ast = parse("""
x = 0
""")
    interpreter.eval(ast, w_model)
    interpreter.space.gc(w_model)
    assert x in interpreter.space.objects

    ast = parse("""
y = x
z = y
""")
    interpreter.eval(ast, w_model)
    interpreter.space.gc(w_model)
    assert x not in interpreter.space.objects


def test_cycle_gc():
    ast = parse("""
object a:
    x = 1
    
object b:
    x = a
    
a x = b
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)
    interpreter.space.gc(w_model)

    a = w_model.getvalue("a")
    b = w_model.getvalue("b")
    assert a in interpreter.space.objects
    assert b in interpreter.space.objects

    ast = parse("""
a = 0
""")
    interpreter.eval(ast, w_model)
    interpreter.space.gc(w_model)

    assert a in interpreter.space.objects
    assert b in interpreter.space.objects

    ast = parse("""
b = 0
""")
    interpreter.eval(ast, w_model)
    interpreter.space.gc(w_model)

    assert a not in interpreter.space.objects
    assert b not in interpreter.space.objects


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
    interpreter.space.gc(w_model)

    a = w_model.getvalue("x").getvalue("a")
    b = w_model.getvalue("x").getvalue("b")
    c = w_model.getvalue("x").getvalue("c")
    x = w_model.getvalue("x")
    assert a in interpreter.space.objects
    assert b in interpreter.space.objects
    assert c in interpreter.space.objects
    assert x in interpreter.space.objects

    ast = parse("""
x = 0
""")
    interpreter.eval(ast, w_model)
    interpreter.space.gc(w_model)
    assert a not in interpreter.space.objects
    assert b not in interpreter.space.objects
    assert c not in interpreter.space.objects
    assert x not in interpreter.space.objects


def test_method_gc():
    ast = parse("""
def meth:
    1
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)
    interpreter.space.gc(w_model)

    meth = w_model.getvalue("meth")
    assert meth in interpreter.space.objects

    ast = parse("""
def meth:
    2
""")
    interpreter.eval(ast, w_model)

    assert meth in interpreter.space.objects

    interpreter.space.gc(w_model)

    assert meth not in interpreter.space.objects


def test_simple_call_gc():
    ast = parse("""
x = 1
gc
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    x = w_model.getvalue("x")
    assert x in interpreter.space.objects

    ast = parse("""
x = 2
""")
    interpreter.eval(ast, w_model)

    assert x in interpreter.space.objects

    ast = parse("""
gc
""")
    interpreter.eval(ast, w_model)

    assert x not in interpreter.space.objects
