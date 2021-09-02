from c3computation import compute_C3_mro as c3


class AbstractObject(object):
    def __init__(self):
        self.mark = False  # gc marker

    def call(self, w_receiver, args_w):
        return self

    def istrue(self):
        return True

    def clone(self):
        raise NotImplementedError

    def hasslot(self, value):
        raise NotImplementedError

    def getvalue(self, name):
        for obj in self.get_mro():
            if not obj.hasslot(name):
                continue
            return obj.slots[name]

    def get_mro(self):
        return c3(self)


class W_NormalObject(AbstractObject):
    def __init__(self, name=None, slots=None, parents=None, space=None):
        super().__init__()
        self.space = space
        self.name = name
        if slots:
            self.slots = slots
        else:
            self.slots = {}
        if parents is None:
            parents = []
        if len(parents) > 0:
            for x in parents:
                assert x in slots
        self.parents = parents

    def getparents(self):
        parents = self.parents
        if '__parent__' not in parents:
            parents.append('__parent__')
        return [self.slots[p] for p in parents if p in self.slots]

    def hasslot(self, name):
        return name in self.slots

    def setvalue(self, name, w_value):
        self.slots[name] = w_value

    def addparent(self, name):
        self.parents.append(name)

    def __str__(self):
        return self.getname()

    __repr__ = __str__

    def getname(self):
        return "<Object {name} {slots}>".format(
            name=self.name if self.name else '',
            slots=self.slots)

    def clone(self):
        return W_NormalObject(
            name=self.name,
            parents=self.parents,
            slots=self.slots.copy())


# Project -----
class PrimitiveObject(AbstractObject):
    def __init__(self, value, trait, space=None):
        super().__init__()
        self.value = value
        self._trait = trait
        self.space = space

    def getparents(self):
        if self.space is None:
            return []  # for tests
        trait = self.space.getbuiltin(self._trait)
        assert trait is not None, 'O_o bogus state'
        return [trait]

    def hasslot(self, name):
        return False

    def __str__(self):
        return str(self.value)

    __repr__ = __str__

    def istrue(self):
        return bool(self.value)


class W_Integer(PrimitiveObject):
    def __init__(self, value, space=None):
        super().__init__(int(value), "inttrait", space=space)


class W_Boolean(PrimitiveObject):
    def __init__(self, value, space=None):
        super().__init__(int(value), "booltrait", space=space)

    def __str__(self):
        return str(bool(self.value))  # true instead of 1

    __repr__ = __str__


class W_String(PrimitiveObject):
    def __init__(self, value, space=None):
        super().__init__(str(value), "strtrait", space=space)


class W_Double(PrimitiveObject):
    def __init__(self, value, space=None):
        super().__init__(float(value), "doubletrait", space=space)


# -------------


class W_Method(W_NormalObject):
    def __init__(self, code, *args, **kwargs):
        super(W_Method, self).__init__(*args, **kwargs)
        self.code = code

    def clone(self):
        return W_Method(code=self.code,
                        name=self.name, parents=self.parents,
                        slots=self.slots.copy())

    def getname(self):
        return "<W_Method({name})>".format(name=self.name)

    def call(self, w_receiver, args_w):
        w_context = self.clone()
        assert len(args_w) == self.code.numargs
        for i in range(self.code.numargs):
            self.space.setvalue(w_context, self.code.symbols[i], args_w[i])
        self.space.setvalue(w_context, 'self', w_receiver)
        return self.space.execute(w_context.code, w_context)
