from objmodel import W_Integer, W_Boolean, W_String
from objmodel import W_Method
from objmodel import W_NormalObject

import primitives


class ObjectSpace(object):

    def __init__(self, interpreter):
        self.interpreter = interpreter

    def setup_builtins(self, builtincode=None):
        if builtincode is None:
            builtincode = self._load_default_builtins()

        w_builtins = W_NormalObject(name='Lobby', slots={})
        self.w_builtins = w_builtins
        from simpleparser import parse
        ast = parse(builtincode)

        self.interpreter.eval(ast, w_builtins)

    def _load_default_builtins(self):
        import os
        builtins = os.path.join(
            os.path.dirname(__file__),
            '../builtins.simple')
        with open(builtins, 'r') as f:
            return f.read()

    def getbuiltin(self, name):
        return self.w_builtins.getvalue(name)

    def getbuiltins(self):
        return self.w_builtins

    def make_module(self, name=None):
        if not hasattr(self, 'w_builtins'):
            slots = {}
        else:
            slots = {'__parent__': self.getbuiltins()}
        return W_NormalObject(name=name, slots=slots)

    def newobject(self, name, slots, parentnames):
        return W_NormalObject(space=self, name=name,
                              slots=slots, parents=parentnames)

    def newint(self, value):
        return W_Integer(value, space=self)

    # Project: Boolean
    def newbool(self, value):
        return W_Boolean(value, space=self)

    # Project: String
    def newstring(self, value):
        return W_String(value, space=self)

    def definemethod(self, name, code, w_target):
        w_meth = W_Method(code, name=name,
                          slots={'__parent__': w_target},
                          space=self)
        return w_meth

    def execute(self, code, w_context):
        return self.interpreter.run(code, w_context)

    def setvalue(self, w_receiver, name, w_value):
        w_receiver.setvalue(name, w_value)

    def addparent(self, w_receiver, name):
        w_receiver.addparent(name)

    def getvalue(self, w_receiver, name):
        return w_receiver.getvalue(name)

    def istrue(self, w_condition):
        return w_condition.istrue()

    def isfalse(self, w_condition):
        return not w_condition.istrue()

    def call_primitive(self, primitive_num, w_receiver, arguments_w):
        f = primitives.all_primitives[primitive_num]
        return f(w_receiver, arguments_w, space=self)

    def get_number_of_arguments_of_primitive(self, primitive_num):
        return primitives.get_number_of_arguments_of_primitive(primitive_num)

    def call(self, w_method, w_receiver, arguments_w):
        return w_method.call(w_receiver, arguments_w)

    def clone(self, w_value):
        return w_value.clone()
