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


def test_rotation():
    w_model, interpreter = eval_test_program("rotations")

    ast = parse("""
x = "Hallo"
y = rotate(x, 2)
z = rotate(x, 4)
""")
    interpreter.eval(ast, w_model)

    assert w_model.getvalue("y").value == "lloHa"
    assert w_model.getvalue("z").value == "oHall"


def test_numbers():
    w_model, interpreter = eval_test_program("numbers")

    ast = parse("""
x = generate_list(5)

def function(n):
    n * n
    
y = generate_list(5)

def function(n):
    n + 1
    
z = generate_list(5)
""")
    interpreter.eval(ast, w_model)

    assert w_model.getvalue("x").value == "1 2 3 4 5"
    assert w_model.getvalue("y").value == "1 4 9 16 25"
    assert w_model.getvalue("z").value == "2 3 4 5 6"
