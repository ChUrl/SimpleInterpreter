from bytecodeinterpreter import Interpreter
from simpleparser import parse


def builtin_test_helper(expr):
    ast = parse("x = " + expr)
    interpreter = Interpreter()
    w_module = interpreter.make_module()
    interpreter.eval(ast, w_module)

    return w_module.getvalue("x").value


def test_sugar_builtins():
    assert builtin_test_helper("2 add(5)") == 7
    assert builtin_test_helper("2 mul(5)") == 10
    assert builtin_test_helper("2 div(5)") == 0
    assert builtin_test_helper("10 div(5)") == 2
    assert builtin_test_helper("10 div(3)") == 3
    assert builtin_test_helper("5 mod(3)") == 2
    assert builtin_test_helper("4 mod(2)") == 0
    assert builtin_test_helper("2 inc") == 3
