from simpleparser import parse
from objmodel import W_NormalObject
from interpreter import Interpreter


#
# The Interpreter class needs a method 'eval(ast, w_context)' that is
# doing "AST visiting", as follows:
#
#     def eval(self, ast, w_context):
#         method = getattr(self, "eval_" + ast.__class__.__name__)
#         return method(ast, w_context)
#
# This calls a method called "eval_Xxx" on self for every class
# called Xxx of the simpleast.py module.
#
def test_simplxe():
    ast = parse("""
10
11
12
""")
    w_module = W_NormalObject()
    interpreter = Interpreter()
    interpreter.eval(ast, w_module)


def test_simple():
    ast = parse("""
k = 10
j = 11
i = 12
""")
    w_module = W_NormalObject()
    interpreter = Interpreter()
    interpreter.eval(ast, w_module)
    assert w_module.getvalue("i").value == 12
    assert w_module.getvalue("j").value == 11
    assert w_module.getvalue("k").value == 10


def test_if():
    ast = parse("""
k = 10
if k:
    j = 11
else:
    i = 12
""")
    w_module = W_NormalObject()
    interpreter = Interpreter()
    interpreter.eval(ast, w_module)
    assert w_module.getvalue("i") is None
    assert w_module.getvalue("j").value == 11
    assert w_module.getvalue("k").value == 10


def test_def():
    ast = parse("""
def f(x, y):
    if x:
        x
    else:
        y
i = f(6, 3)
j = f(0, 9)
""")
    w_module = W_NormalObject()
    interpreter = Interpreter()
    interpreter.eval(ast, w_module)
    assert w_module.getvalue("i").value == 6
    assert w_module.getvalue("j").value == 9


def test_object():
    ast = parse("""
object x:
    i = 4
    j = i
    object z:
        i = 5
""")
    w_module = W_NormalObject()
    interpreter = Interpreter()
    interpreter.eval(ast, w_module)
    assert w_module.getvalue("x").getvalue("i").value == 4
    assert w_module.getvalue("x").getvalue("j").value == 4
    assert w_module.getvalue("x").getvalue("z").getvalue("i").value == 5


def test_obscure_recursion():
    ast = parse("""
object a:
    def f(a):
        if a:
            x = 5
            a f(0)
        else:
            x = 7
        x
i = a f(a)
""")
    w_module = W_NormalObject()
    interpreter = Interpreter()
    interpreter.eval(ast, w_module)
    assert w_module.getvalue("i").value == 5


def test_assign():
    ast = parse("""
object a:
    b = 5
    def set(n):
        self b = n
a set(7)
i = a b
""")
    w_module = W_NormalObject()
    interpreter = Interpreter()
    interpreter.eval(ast, w_module)
    assert w_module.getvalue("i").value == 7
