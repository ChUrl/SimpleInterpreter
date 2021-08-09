"""
A 'simple' parser.  Don't look into this file :-)
"""
import py
import simpleast
from simplelexer import lex
from rply.token import Token

from rply import ParserGenerator

pg = ParserGenerator(["If", "Else", "While", "Def", "Object", "Number",
                      "String", "Name", "Indent", "Dedent", "Newline", "OpenBracket",
                      "CloseBracket", "Comma", "Assign", "Colon", "PrimitiveName", "EOF"])


def build_methodcall(call, cls):
    if len(call) == 1:
        args = []
    else:
        args = call[1]
    name = call[0]
    return cls(None, name, args)


@pg.production("program : statements EOF")
@pg.production("program : newlines statements EOF")
def program(prog):
    # import pdb; pdb.set_trace()
    if prog[0] is None:
        prog = prog[1]
    else:
        prog = prog[0]
    return prog


@pg.production("statements : statement")
@pg.production("statements : statement statements")
@pg.production("statements : statement newlines statements")
def statements(stmts):
    if len(stmts) == 1:
        stmt = stmts[0]
        return simpleast.Program([stmt])
    elif stmts[0] is None:
        assert len(stmts) == 2
        return stmts[1]
    elif len(stmts) == 2:
        stmt = stmts[0]
        result = stmts[1]
        result.statements.insert(0, stmt)
    return result


@pg.production("newlines : Newline")
@pg.production("newlines : Newline newlines")
def newlines(n):
    return None


@pg.production("statement : simplestatement")
@pg.production("statement : ifstatement")
@pg.production("statement : whilestatement")
@pg.production("statement : defstatement")
@pg.production("statement : objectstatement")
def statement(stmt):
    return stmt[0]


@pg.production("ifstatement : If expression block")
@pg.production("ifstatement : If expression block Else block")
def ifstatement(ifstmt):
    elseblock = None
    if len(ifstmt) > 3:
        elseblock = ifstmt[-1]
    return simpleast.IfStatement(ifstmt[1], ifstmt[2], elseblock)


@pg.production("whilestatement : While expression block")
def ifstatement(whilestmt):
    return simpleast.WhileStatement(whilestmt[1], whilestmt[2])


@pg.production("objectstatement : Object name block")
@pg.production("objectstatement : Object name parentlist block")
def objectstatement(obj):
    name = obj[1]
    names = []
    expressions = []
    if len(obj) == 3:
        blk = obj[2]
    else:
        parents = obj[2]
        names = [p.attrname for p in parents]
        expressions = [p.expression for p in parents]
        blk = obj[3]
    return simpleast.ObjectDefinition(name, blk, names, expressions)


@pg.production("defstatement : Def name argumentnamelist block")
@pg.production("defstatement : Def name block")
def defstatement(defn):
    name = defn[1]
    if len(defn) == 4:
        args = defn[2]
        blk = defn[3]
    else:
        args = []
        blk = defn[2]
    return simpleast.FunctionDefinition(name, args, blk)


@pg.production("block : Colon newlines Indent statements Dedent")
def block(blk):
    return blk[3]


@pg.production("simplestatement : expression Newline")
@pg.production("simplestatement : expression Assign expression Newline")
def simplestatement(stmts):
    if len(stmts) == 2:
        return simpleast.ExprStatement(stmts[0])
    # assignement
    result = stmts[0]
    assign = stmts[2]
    if (isinstance(result, simpleast.MethodCall) and
            result.arguments == []):
        return simpleast.Assignment(
            result.receiver, result.methodname, assign)
    else:
        source_pos = stmts[1].source_pos
        raise ParseError(source_pos,
                         ErrorInformation(source_pos.idx,
                                          customerror="can only assign to attribute"))  # , self.source)


@pg.production("expression : basic_expression")
@pg.production("expression : basic_expression msg-chain")
def expression(expr):
    if len(expr) > 1:
        prev = expr[0]
        for i in expr[1]:
            i.receiver = prev
            prev = i
        return expr[1][-1]
    return expr[0]


@pg.production("msg-chain : methodcall")
@pg.production("msg-chain : methodcall msg-chain")
def msg_chain(cc):
    if len(cc) > 1:
        return [cc[0]] + cc[1]
    return cc


@pg.production("basic_expression : Number")
def number_expression(stmt):
    return simpleast.IntLiteral(stmt[0].value)


@pg.production("basic_expression : String")
def string_expression(stmt):
    return simpleast.StringLiteral(stmt[0].value)


@pg.production("basic_expression : implicitselfmethodcall")
def implicitselfmethodcall(call):
    methodcall = call[0]
    methodcall.receiver = simpleast.ImplicitSelf()
    return methodcall


@pg.production("implicitselfmethodcall : methodcall")
def implicitselfmethodcall_methodcall(call):
    return call[0]


@pg.production("methodcall : primitivemethodcall")
@pg.production("methodcall : simplemethodcall")
def methodcall(call):
    return call[0]


@pg.production("simplemethodcall : name")
@pg.production("simplemethodcall : name argumentslist")
def simplemethodcall(call):
    return build_methodcall(call, simpleast.MethodCall)


@pg.production("primitivemethodcall : primitivename")
@pg.production("primitivemethodcall : primitivename argumentslist")
def primitivemethodcall(call):
    return build_methodcall(call, simpleast.PrimitiveMethodCall)


@pg.production("argumentslist : OpenBracket arguments CloseBracket")
@pg.production("argumentnamelist : OpenBracket argumentnames CloseBracket")
@pg.production("parentlist : OpenBracket parentdefinitions CloseBracket")
def argumentslist(args):
    return args[1]


@pg.production("arguments : expression")
@pg.production("arguments : expression Comma")
@pg.production("arguments : expression Comma arguments")
@pg.production("argumentnames : name")
@pg.production("argumentnames : name Comma")
@pg.production("argumentnames : name Comma argumentnames")
@pg.production("parentdefinitions : assignment")
@pg.production("parentdefinitions : assignment Comma")
@pg.production("parentdefinitions : assignment Comma parentdefinitions")
def arguments(args):
    if len(args) == 3:
        return [args[0]] + args[2]
    return [args[0]]


@pg.production("assignment : name Assign expression")
def assignement(args):
    return simpleast.Assignment(None, args[0], args[2])


@pg.production("primitivename : PrimitiveName")
@pg.production("name : Name")
def name(name):
    return name[0].value


@pg.error
def error_handler(token):
    raise ParseError(source_pos=token.getsourcepos(),
                     errorinformation=ErrorInformation(token.getsourcepos().idx,
                                                       customerror="Ran into a %s where it wasn't expected" % token.gettokentype()))


parser = pg.build()


def print_conflicts():
    print("rr conflicts")
    for rule_num, token, conflict in parser.lr_table.rr_conflicts:
        print(rule_num, token, conflict)

    print("sr conflicts")
    for rule_num, token, conflict in parser.lr_table.sr_conflicts:
        print(rule_num, token, conflict)


print_conflicts()


def parse(s):
    l = lex(s)
    return parser.parse(iter(l))


# ____________________________________________________________

class ParseError(Exception):
    def __init__(self, source_pos, errorinformation, source=""):
        self.source_pos = source_pos
        self.errorinformation = errorinformation
        self.args = (source_pos, errorinformation)
        self.source = source

    def nice_error_message(self, filename="<unknown>"):
        result = ["  File %s, line %s" % (filename, self.source_pos.lineno + 1)]
        source = self.source
        if source:
            result.append(source.split("\n")[self.source_pos.lineno])
            result.append(" " * self.source_pos.colno + "^")
        else:
            result.append("<couldn't get source>")
        result.append("ParseError")
        if self.errorinformation:
            failure_reasons = self.errorinformation.expected
            if failure_reasons:
                expected = ''
                if len(failure_reasons) > 1:
                    all_but_one = failure_reasons[:-1]
                    last = failure_reasons[-1]
                    expected = "%s or '%s'" % (
                        ", ".join(["'%s'" % e for e in all_but_one]), last)
                elif len(failure_reasons) == 1:
                    expected = failure_reasons[0]
                if expected:
                    result.append("expected %s" % (expected,))
            if self.errorinformation.customerror:
                result.append(self.errorinformation.customerror)
        return "\n".join(result)

    def __str__(self):
        return self.nice_error_message()


class ErrorInformation(object):
    def __init__(self, pos, expected=None, customerror=None):
        if expected is None:
            expected = []
        self.expected = expected
        self.pos = pos
        self.customerror = customerror


def combine_errors(self, other):
    if self is None:
        return other
    if (other is None or self.pos > other.pos or
            len(other.expected) == 0):
        return self
    elif other.pos > self.pos or len(self.expected) == 0:
        return other
    failure_reasons = []
    already_there = {}
    for fr in [self.expected, other.expected]:
        for reason in fr:
            if reason not in already_there:
                already_there[reason] = True
                failure_reasons.append(reason)
    return ErrorInformation(self.pos, failure_reasons,
                            self.customerror or other.customerror)


def make_arglist(methodname):
    def arglist(self):
        self.match("OpenBracket", "(")
        method = getattr(self, methodname)
        result = [method()]
        result.extend(self.repeat(self.comma, method))
        self.maybe(self.comma)
        self.match("CloseBracket", ")")
        return result

    return arglist
