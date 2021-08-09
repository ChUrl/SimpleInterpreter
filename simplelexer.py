from rply import LexerGenerator
from rply.token import Token

# attempts at writing a simple Python-like lexer
tabsize = 4


def make_indent_token(token, start):
    assert token.name == "NewlineAndWhitespace"
    token.name = "Indent"
    token.value = token.value[start:]
    token.source_pos.idx += start
    token.source_pos.lineno += 1
    token.source_pos.colno = 0
    return token


def make_dedent_token(token, start):
    assert token.name == "NewlineAndWhitespace"
    token.name = "Dedent"
    token.value = token.value[start:]
    token.source_pos.idx += start
    token.source_pos.lineno += 1
    token.source_pos.colno = 0
    return token


# split the token in two: one for the newline and one for the
# in/dedent
# the NewlineAndWhitespace token looks like this: \r?\n[ \f\t]*
def compute_position_of_newline(token):
    assert token.name == "NewlineAndWhitespace"
    s = token.value
    length = len(s)
    pos = 0
    column = 0
    if s[0] == '\n':
        pos = 1
        start = 1
    else:
        pos = 2
        start = 2
    while pos < length:  # count the indentation depth of the whitespace
        c = s[pos]
        if c == ' ':
            column = column + 1
        elif c == '\t':
            column = (column // tabsize + 1) * tabsize
        elif c == '\f':
            column = 0
        pos = pos + 1
    return start, column


def compute_indent_or_dedent(token, indentation_levels, output_tokens):
    start, column = compute_position_of_newline(token)
    # before start: new line token 
    output_tokens.append(Token("Newline", token.value[:start], token.source_pos))
    # after start: deal with white spaces (create indent or dedent token)
    if column > indentation_levels[-1]:  # count indents or dedents
        indentation_levels.append(column)
        token = make_indent_token(token, start)
        output_tokens.append(token)
    else:
        dedented = False
        while column < indentation_levels[-1]:
            dedented = True
            indentation_levels.pop()
            output_tokens.append(Token("Dedent", "",
                                       token.source_pos))
        if dedented:
            token = make_dedent_token(token, start)
            output_tokens[-1] = token


# input: lexer token stream
# output: modified token stream
def postprocess(tokens, source):
    parenthesis_level = 0
    indentation_levels = [0]
    output_tokens = []
    tokens = [token for token in tokens if token.name != "Ignore"]
    token = None
    for i in range(len(tokens)):
        token = tokens[i]
        # never create indent/dedent token between brackets 
        if token.name == "OpenBracket":
            parenthesis_level += 1
            output_tokens.append(token)
        elif token.name == "CloseBracket":
            parenthesis_level -= 1
            if parenthesis_level < 0:
                raise LexerError(source, token.source_pos, "unmatched parenthesis")
            output_tokens.append(token)
        elif token.name == "NewlineAndWhitespace":
            if i + 1 < len(tokens) and tokens[i + 1].name == "NewlineAndWhitespace":
                continue
            if parenthesis_level == 0:
                compute_indent_or_dedent(token, indentation_levels, output_tokens)
            else:
                pass  # implicit line-continuations within parenthesis
        else:
            # something else: e.g. name, keyword, etc...
            output_tokens.append(token)
    if token is not None:
        output_tokens.append(Token("EOF", "", token.source_pos))
    return output_tokens


# RPython reimplementation
def group(*choices, **namegroup):
    choices = list(choices)
    return '(' + '|'.join(choices) + ')'


# RPython reimplementation
def any(*choices):
    result = group(*choices) + '*'
    return result


# ' or " string. eg. 'hello' or "hello"
def make_single_string(delim):
    normal_chars = r"[^\n\%s]*" % (delim,)
    return "".join([delim, normal_chars,
                    any(r"\\." + normal_chars), delim])


# ____________________________________________________________
# Literals

Number = r'(([+-])?[1-9][0-9]*)|0'
String = group(make_single_string(r"\'"), make_single_string(r'\"'))

# ____________________________________________________________
# Ignored

Whitespace = r'[ \f\t]'
Newline = r'\r?\n'
Linecontinue = r'\\' + Newline
Comment = r'#[^\r\n]*'
NewlineAndWhitespace = Newline + any(Whitespace)
Ignore = group(Whitespace + '+', Linecontinue, Comment)

# ____________________________________________________________
# Identifier

Name = r'[a-zA-Z_][a-zA-Z0-9_]*'
PrimitiveName = '\\$' + Name

# ____________________________________________________________
# Symbols

Colon = r'\:'
Comma = r'\,'
Assign = r'\='

OpenBracket = r'[\[\(\{]'
CloseBracket = r'[\]\)\}]'

# ____________________________________________________________
# Keywords

If = r'if'
Else = r'else'
While = r'while'
Def = r'def'
Object = r'object'

tokens = ["If", "Else", "While", "Def", "Object", "Number", "String", "Ignore",
          "NewlineAndWhitespace", "OpenBracket", "CloseBracket", "Comma", "Assign",
          "Colon", "Name", "PrimitiveName"]


def make_lexer():
    lg = LexerGenerator()
    for token in tokens:
        # e.g. (Name, r'[a-zA-Z_][a-zA-Z0-9_]*')
        lg.add(token, globals()[token])
    return lg.build()


lexer = make_lexer()


# s is the simple program code
def lex(s):
    if not s.endswith('\n'):
        s += '\n'
    return list(postprocess(lexer.lex(s), s))
