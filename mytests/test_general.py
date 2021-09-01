from bytecodeinterpreter import Interpreter
from simpleparser import parse


def eval_test_program(name):
    import os
    program = os.path.join(os.path.dirname(__file__),
                           "..",
                           "examples",
                           name + ".simple")

    with open(program, "r") as f:
        ast = parse(f.read())
        interpreter = Interpreter()
        w_model = interpreter.make_module()
        interpreter.eval(ast, w_model)

        return w_model, interpreter


def test_fibonacci_rec():
    w_model, interpreter = eval_test_program("fibonacci")

    ast = parse("""
x = fibonacci_rec(5)
y = fibonacci_rec(10)
""")
    interpreter.eval(ast, w_model)

    assert w_model.getvalue("x").value == 5
    assert w_model.getvalue("y").value == 55

    ast = parse("""
x = fibonacci_it(5)
y = fibonacci_it(10)
""")
    interpreter.eval(ast, w_model)

    assert w_model.getvalue("x").value == 5
    assert w_model.getvalue("y").value == 55


def test_inheritance():
    w_model, interpreter = eval_test_program("inheritance")

    ast = parse("""
x = square
x size = 5
xa = x area

y = circle
ya = y area
""")
    interpreter.eval(ast, w_model)

    assert w_model.getvalue("xa").value == 25
    assert w_model.getvalue("ya").value == 3.1415
