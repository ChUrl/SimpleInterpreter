from rply import Token

from simpleast import Program, ExprStatement, BooleanLiteral, ImplicitSelf, Assignment, StringLiteral
from simplelexer import lex
from simpleparser import parse
from objmodel import W_NormalObject, W_Integer, W_String, W_Boolean
from interpreter import Interpreter


def test_basic_string_lexing():
    assert lex("\"Hallo\"")[0] == Token("String", "\"Hallo\"")
    assert lex("\'Hallo\'")[0] == Token("String", "\'Hallo\'")
    assert lex("x = \"true\"")[:3] == [Token("Name", "x"), Token("Assign", "="), Token("String", "\"true\"")]


def test_basic_string_parsing():
    assert parse("\"false\"") == Program([ExprStatement(StringLiteral("false"))])
    assert parse("x = \"false\"") == Program([Assignment(ImplicitSelf(), "x", StringLiteral("false"))])


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
w = "Hallo" eq("Hallo")
x = "Hallo" add("ollaH")
y = "Hallo" rev
z = "Hallo" len
""")
    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    assert isinstance(w_model.getvalue("w"), W_Boolean)
    assert w_model.getvalue("w").istrue() is True
    assert isinstance(w_model.getvalue("x"), W_String)
    assert w_model.getvalue("x").value == "HalloollaH"
    assert isinstance(w_model.getvalue("y"), W_String)
    assert w_model.getvalue("y").value == "ollaH"
    assert isinstance(w_model.getvalue("z"), W_Integer)
    assert w_model.getvalue("z").value == 5


def test_string_conversion():
    ast = parse("""
w = "true" tobool
x = true tostr
y = 25 tostr
z = "25" toint
""")

    interpreter = Interpreter()
    w_model = interpreter.make_module()
    interpreter.eval(ast, w_model)

    assert isinstance(w_model.getvalue("w"), W_Boolean)
    assert w_model.getvalue("w").istrue() is True
    assert isinstance(w_model.getvalue("x"), W_String)
    assert w_model.getvalue("x").value == "true"
    assert isinstance(w_model.getvalue("y"), W_String)
    assert w_model.getvalue("y").value == "25"
    assert isinstance(w_model.getvalue("z"), W_Integer)
    assert w_model.getvalue("z").value == 25
