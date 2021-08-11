import py

from simpleparser import ParseError, parse
from simplelexer import lex
from simpleast import *

def raisesparserror(source):
    with py.test.raises(ParseError) as excinfo:
        parse(source)
    print(excinfo.value.nice_error_message())


def test_expression():
    ast = parse("a b c")
    ast1 = MethodCall(MethodCall(MethodCall(ImplicitSelf(), "a"), "b"), "c")
    assert ast == Program([ExprStatement(ast1)])
    ast = parse("a f(1, a b c, 3,)")
    ast2 = Program([ExprStatement(MethodCall(MethodCall(ImplicitSelf(), "a"), "f", [
                      IntLiteral(1), ast1, IntLiteral(3)]))])
    assert ast == ast2


def test_expression2():
    ast = parse("$a $b $c")
    ast1 = PrimitiveMethodCall(PrimitiveMethodCall(
        PrimitiveMethodCall(ImplicitSelf(), "$a"), "$b"), "$c")
    assert ast == Program([ExprStatement(ast1)])
    ast = parse("$a $f(1, $a $b $c, 3,)")
    assert ast == Program([ExprStatement(PrimitiveMethodCall(
            PrimitiveMethodCall(ImplicitSelf(), "$a"), "$f", [
                      IntLiteral(1), ast1, IntLiteral(3)]))])


def test_simplestatement():
    ast = parse("a\n")
    ast1 = Program([ExprStatement(MethodCall(ImplicitSelf(), "a"))])
    assert ast == ast1
    ast = parse("a = 4 b\n")
    ast1 = Program([Assignment(ImplicitSelf(), "a", MethodCall(IntLiteral(4), "b"))])
    assert ast == ast1
    ast = raisesparserror("a(1) = 4 b\n")
    ast = raisesparserror("1 = 4 b\n")

def test_error():
    ast = raisesparserror("a add 2\n")



def test_if():
    ast = parse("""if a and(b):
    a b
""")
    ast1 = Program([IfStatement(MethodCall(MethodCall(ImplicitSelf(), "a"), "and",
                                  [MethodCall(ImplicitSelf(), "b")]),
                       Program([ExprStatement(
                           MethodCall(MethodCall(ImplicitSelf(), "a"),
                                "b"))]))])
    assert ast1 == ast

    ast = parse("""if a and(b):
    a b
else:
    b
""")
    ast1 = Program([IfStatement(MethodCall(MethodCall(ImplicitSelf(), "a"), "and",
                                  [MethodCall(ImplicitSelf(), "b")]),
                       Program([ExprStatement(
                           MethodCall(MethodCall(ImplicitSelf(), "a"),
                                "b"))]),
                       Program([ExprStatement(
                           MethodCall(ImplicitSelf(), "b"))]))])
    assert ast1 == ast

def test_while():
    ast = parse("""
while i:
    i = i sub(1)
""")
    ast1 = Program([WhileStatement(MethodCall(ImplicitSelf(), "i"),
                          Program([Assignment(ImplicitSelf(), "i",
                                      MethodCall(MethodCall(ImplicitSelf(), "i"),
                                                 "sub",
                                                 [IntLiteral(1)]))]))])
    assert ast1 == ast

def test_object():
    ast = parse("""
object a:
    i = 1
    if i:
        j = 2
""")
    ast1 = Program([ObjectDefinition("a", Program([
        Assignment(ImplicitSelf(), "i", IntLiteral(1)),
        IfStatement(MethodCall(ImplicitSelf(), "i"), Program([
            Assignment(ImplicitSelf(), "j", IntLiteral(2)),
            ]))
        ]))])
    assert ast1 == ast

    ast = parse("""
object a(parent=1):
    i = 1
    if i:
        j = 2
""")
    ast1 = Program([ObjectDefinition("a", Program([
        Assignment(ImplicitSelf(), "i", IntLiteral(1)),
        IfStatement(MethodCall(ImplicitSelf(), "i"), Program([
            Assignment(ImplicitSelf(), "j", IntLiteral(2)),
            ]))
        ]),
        ["parent"],
        [IntLiteral(1)])])
    assert ast1 == ast


def test_def():
    ast = parse("""
def f(x, y, z):
    i = 1
    if i:
        j = 2
""")
    ast1 = Program([FunctionDefinition("f", ["x", "y", "z"], Program([
        Assignment(ImplicitSelf(), "i", IntLiteral(1)),
        IfStatement(MethodCall(ImplicitSelf(), "i"), Program([
            Assignment(ImplicitSelf(), "j", IntLiteral(2)),
            ]))
        ]))])
    assert ast1 == ast


def test_object2():
    ast = parse("""
object None:
    1
""")
    ast = parse("""
def pass:
    None
""")
    ast = parse("""
object None:
    1

def pass:
    None
""")
