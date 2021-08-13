from rply import Token
from simplelexer import lex


def test_lexing():
    token = lex("+ - * / ++ %")

    assert Token("Plus", "+") == token[0]
    assert Token("Minus", "-") == token[1]
    assert Token("Multiply", "*") == token[2]
    assert Token("Divide", "/") == token[3]
    assert Token("Increment", "++") == token[4]
    assert Token("Modulo", "%") == token[5]
