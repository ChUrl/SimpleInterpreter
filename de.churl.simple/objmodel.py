from c3computation import compute_C3_mro as c3


class AbstractObject(object):

    def call(self, w_receiver, args_w):
        return self

    def istrue(self):
        return True

    def clone(self):
        raise NotImplementedError

    def hasslot(self):
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


class W_Integer(AbstractObject):
    def __init__(self, value, space=None, trait="inttrait"):
        self.value = int(value)
        self.space = space
        self.__trait = trait  # used this to extend from W_Integer

    def getparents(self):
        if self.space is None:
            return []  # for tests
        trait = self.space.getbuiltin(self.__trait)
        assert trait is not None, 'O_o bogus state'
        return [trait]

    def hasslot(self, name):
        return False

    def __str__(self):
        return str(self.value)

    __repr__ = __str__

    def istrue(self):
        return self.value != 0


# Project: Boolean
class W_Boolean(W_Integer):  # don't know if extending is good idea
    def __init__(self, value, space=None):
        super().__init__(int(value), space=space, trait="booltrait")


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
