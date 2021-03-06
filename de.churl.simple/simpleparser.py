"""
A 'simple' parser.  Don't look into this file :-)
"""
from rply import ParserGenerator, Token
from simplelexer import lex
import simpleast

pg = ParserGenerator(["If", "Else", "While", "Def", "Object", "Number",
                      "String", "Boolean", "Double",
                      "GC",
                      "Name", "Indent", "Dedent", "Newline", "OpenBracket",
                      "CloseBracket", "Comma", "Colon",
                      "Increment", "Plus", "Minus", "Multiply", "Divide", "Modulo",
                      "Decrement", "PlusInplace", "MinusInplace", "MultiplyInplace", "DivideInplace",
                      "Less", "LessEqual", "Greater", "GreaterEqual", "Equal", "NotEqual",
                      "Assign",
                      "And", "Or",
                      "PrimitiveName", "EOF",
                      "Not"],
                     # Operator precedence for ambiguous rules, ascending
                     precedence=[("left", ["Or"]),
                                 ("left", ["And"]),
                                 ("left", ["Equal", "NotEqual"]),
                                 ("left", ["Less", "LessEqual", "Greater", "GreaterEqual"]),
                                 ("left", ["Plus", "Minus"]),
                                 ("left", ["Multiply", "Divide", "Modulo"]),
                                 ("left", ["Not"]),
                                 ("left", ["Increment", "Decrement"])])


def build_methodcall(call, cls, receiver=None):
    if len(call) == 1:
        args = []
    else:
        args = call[1]
    name = call[0]

    return cls(receiver, name, args)


@pg.production("program : statements EOF")
@pg.production("program : newlines statements EOF")
def program(prog):
    # import pdb; pdb.set_trace()
    if prog[0] is None:  # source starts with newlines
        prog = prog[1]
    else:
        prog = prog[0]

    return prog


@pg.production("statements : statement")
@pg.production("statements : statement statements")
@pg.production("statements : statement newlines statements")
def statements(stmts):
    if len(stmts) == 1:  # single statement
        stmt = stmts[0]
        return simpleast.Program([stmt])
    elif stmts[0] is None:  # ?
        assert len(stmts) == 2
        return stmts[1]
    elif len(stmts) == 2:  # merge programs (simpleast.Program)
        stmt = stmts[0]
        result = stmts[1]
        result.statements.insert(0, stmt)

    return result


@pg.production("newlines : Newline")
@pg.production("newlines : Newline newlines")
def newlines(n):
    return None


@pg.production("statement : GC newlines")
@pg.production("statement : GC")
def gcstatement(stmt):
    return simpleast.GCStatement()


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
        parents = obj[2]  # list of assignments (simpleast.Assignment)
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

    # assignment
    result = stmts[0]
    assign = stmts[2]
    if isinstance(result, simpleast.MethodCall) and result.arguments == []:  # assign to attribute
        return simpleast.Assignment(result.receiver, result.methodname, assign)

    source_pos = stmts[1].source_pos
    raise ParseError(source_pos,
                     ErrorInformation(source_pos.idx,
                                      customerror="can only assign to attribute"))  # , self.source)


@pg.production("expression : basic_expression")
@pg.production("expression : basic_expression msg-chain")
def expression(expr):
    if len(expr) > 1:  # expression has messages
        prev = expr[0]
        for i in expr[1]:  # reverse message order
            i.receiver = prev
            prev = i
        return expr[1][-1]  # return last message

    return expr[0]


# Project: Sugar
@pg.production("expression : expression Plus expression")
@pg.production("expression : expression Minus expression")
@pg.production("expression : expression Multiply expression")
@pg.production("expression : expression Divide expression")
@pg.production("expression : expression Modulo expression")
def sugar_binary_arithmetic(expr):
    op = {
        "Plus": "add",
        "Minus": "sub",
        "Multiply": "mul",
        "Divide": "div",
        "Modulo": "mod",
    }[expr[1].name]

    return build_methodcall([op, [expr[2]]], simpleast.MethodCall, expr[0])  # ([name, arg], class, receiver)


@pg.production("expression : expression Decrement expression")
@pg.production("expression : expression Decrement")
@pg.production("expression : expression Increment expression")
@pg.production("expression : expression Increment")
@pg.production("expression : expression PlusInplace expression")
@pg.production("expression : expression MinusInplace expression")
@pg.production("expression : expression MultiplyInplace expression")
@pg.production("expression : expression DivideInplace expression")
def sugar_inplace_arithmetic(expr):
    op = {
        "Increment": "inc",
        "Decrement": "dec",
        "PlusInplace": "add",
        "MinusInplace": "sub",
        "MultiplyInplace": "mul",
        "DivideInplace": "div",
    }[expr[1].name]
    args = [] if len(expr) == 2 else [expr[2]]  # unary/binary
    methcall = build_methodcall([op, args], simpleast.MethodCall, expr[0])

    if isinstance(expr[0], simpleast.MethodCall) and expr[0].arguments == []:  # attribute
        return simpleast.Assignment(expr[0].receiver, expr[0].methodname, methcall)  # modify inplace

    return build_methodcall([op, args], simpleast.MethodCall, expr[0])  # just increment


@pg.production("expression : expression Less expression")
@pg.production("expression : expression LessEqual expression")
@pg.production("expression : expression Greater expression")
@pg.production("expression : expression GreaterEqual expression")
@pg.production("expression : expression Equal expression")
@pg.production("expression : expression NotEqual expression")
def sugar_comparison(expr):
    op = {
        "Less": "less",
        "LessEqual": "leq",
        "Greater": "greater",
        "GreaterEqual": "geq",
        "Equal": "eq",
        "NotEqual": "noteq",
    }[expr[1].name]

    return build_methodcall([op, [expr[2]]], simpleast.MethodCall, expr[0])  # ([name, arg], class, receiver)


@pg.production("expression : expression And expression")
@pg.production("expression : expression Or expression")
@pg.production("expression : Not expression")
def sugar_logical(expr):
    if len(expr) == 2:  # unary
        return build_methodcall(["not", []], simpleast.MethodCall, expr[1])

    op = {
        "And": "and",
        "Or": "or",
    }[expr[1].name]

    return build_methodcall([op, [expr[2]]], simpleast.MethodCall, expr[0])  # ([name, arg], class, receiver)


@pg.production("expression : OpenBracket expression CloseBracket")
def sugar_parenthesis(expr):
    return expr[1]


@pg.production("msg-chain : methodcall")
@pg.production("msg-chain : methodcall msg-chain")
def msg_chain(cc):
    if len(cc) > 1:
        return [cc[0]] + cc[1]  # merge message lists for chain

    return cc


@pg.production("basic_expression : Number")
def number_expression(stmt):
    return simpleast.IntLiteral(stmt[0].value)


@pg.production("basic_expression : Boolean")
def boolean_expression(stmt):
    return simpleast.BooleanLiteral(stmt[0].value)


@pg.production("basic_expression : String")
def string_expression(stmt):
    return simpleast.StringLiteral(stmt[0].value[1:-1])  # cut off delimiters


@pg.production("basic_expression : Double")
def double_expression(stmt):
    return simpleast.DoubleLiteral(stmt[0].value)


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
        return [args[0]] + args[2]  # merge argument lists for chain

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
