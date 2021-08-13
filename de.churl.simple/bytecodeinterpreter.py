from simpleparser import parse
from objspace import ObjectSpace
import compile
from disass import disassemble


class ByteCodeError(Exception):
    pass


class Interpreter(object):

    def __init__(self, builtincode=None):
        # Using an instance variable to keep the public interface
        self.space = ObjectSpace(self)
        self.space.setup_builtins(builtincode)

    def eval(self, ast, w_context):
        code = compile.compile(ast)
        return self.run(code, w_context)

    def read4(self, code, pc):
        """ Converts 4 unicode characters to single 4 byte value """
        highval = ord(code[pc + 3])  # most significant byte
        if highval >= 128:  # convert from 2's complement?
            highval -= 256
        return (ord(code[pc]) |  # merge single bytes into 4 byte value
                (ord(code[pc + 1]) << 8) |
                (ord(code[pc + 2]) << 16) |
                (highval << 24))

    def run(self, bytecode, w_context):
        pc = 0
        stack = []
        code = bytecode.code
        print(disassemble(bytecode))
        while pc < len(code):
            opcode = ord(code[pc])  # convert unicode to number
            pc += 1
            if compile.isjump(opcode):
                oparg = self.read4(code, pc)
                pc += 4
                if opcode == compile.JUMP:
                    pc += oparg
                elif opcode == compile.JUMP_IF_FALSE:
                    w_condition = stack.pop()
                    if self.space.isfalse(w_condition):
                        pc += oparg
                continue
            elif compile.hasarg(opcode):
                oparg = ord(code[pc])
                pc += 1
                if oparg >= 128:
                    if oparg > 128:
                        oparg -= 256
                    else:
                        oparg = self.read4(code, pc)
                        pc += 4
                if opcode == compile.MAKE_OBJECT:
                    name = bytecode.symbols[oparg]
                    obj = self.space.newobject(name, {'__parent__': w_context}, [])
                    stack.append(obj)
                elif opcode == compile.MAKE_OBJECT_CALL:
                    self.run(bytecode.subbytecodes[oparg], stack[-1])
                elif opcode == compile.INT_LITERAL:
                    w_value = self.space.newint(oparg)
                    stack.append(w_value)
                elif opcode == compile.BOOL_LITERAL:  # Project: Boolean
                    w_value = self.space.newbool(oparg)  # oparg is 1 or 0
                    stack.append(w_value)
                elif opcode == compile.STRING_LITERAL:  # Project: String
                    value = bytecode.symbols[oparg]
                    w_value = self.space.newstring(value)
                    stack.append(w_value)
                elif opcode == compile.MAKE_FUNCTION:
                    bc = bytecode.subbytecodes[oparg]
                    w_method = self.space.definemethod(name=bc.name, code=bc, w_target=w_context)
                    stack.append(w_method)
                elif opcode == compile.METHOD_LOOKUP:
                    name = bytecode.symbols[oparg]
                    w_method = self.space.getvalue(stack[-1], name)
                    stack.append(w_method)
                elif opcode == compile.METHOD_CALL:
                    arguments_w = [stack.pop() for n in range(oparg)]
                    arguments_w.reverse()
                    #
                    w_method = stack.pop()
                    w_receiver = stack.pop()
                    w_result = self.space.call(w_method, w_receiver, arguments_w)
                    stack.append(w_result)
                elif opcode == compile.PRIMITIVE_METHOD_CALL:
                    nargs = self.space.get_number_of_arguments_of_primitive(oparg)
                    arguments_w = [stack.pop() for n in range(nargs)]
                    arguments_w.reverse()
                    w_receiver = stack.pop()
                    w_result = self.space.call_primitive(oparg, w_receiver, arguments_w)
                    stack.append(w_result)
                elif opcode == compile.SET_LOCAL:
                    w_value = stack[-1]
                    name = bytecode.symbols[oparg]
                    self.space.setvalue(w_context, name, w_value)
                elif opcode == compile.ASSIGNMENT:
                    w_value = stack.pop()
                    name = bytecode.symbols[oparg]
                    self.space.setvalue(stack[-1], name, w_value)
                elif opcode == compile.ASSIGNMENT_APPEND_PARENT:
                    w_value = stack.pop()
                    name = bytecode.symbols[oparg]
                    self.space.setvalue(stack[-1], name, w_value)
                    self.space.addparent(stack[-1], name)
                elif opcode == compile.GET_LOCAL:
                    name = bytecode.symbols[oparg]
                    w_value = self.space.getvalue(w_context, name)
                    w_value = self.space.call(w_value, w_context, [])
                    stack.append(w_value)
                else:
                    raise ByteCodeError('Invalid bytecode with arguments')
            else:
                if opcode == compile.POP:
                    stack.pop()
                elif opcode == compile.IMPLICIT_SELF:
                    stack.append(w_context)
                elif opcode == compile.DUP:
                    stack.append(stack[-1])
                else:
                    raise ByteCodeError('Invalid bytecode')
        assert pc == len(code)
        assert len(stack) == 1
        return stack.pop()

    def make_module(self):
        return self.space.make_module()
