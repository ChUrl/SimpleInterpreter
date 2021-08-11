registry = {}
all_primitives = []
primitive_number_of_arguments = []


def primitive(name, unwrap_spec, wrap_spec):
    assert '$' + name not in registry, '${name} already defined'.format(name=name)
    primitive_number_of_arguments.append(len(unwrap_spec) - 1)  # first argument is the receiver

    def expose(func):
        def unwrapper(w_receiver, args_w, space):
            args = [w_receiver] + args_w
            if len(args) != len(unwrap_spec):
                raise TypeError(
                    "Expected {ex} arguments, received {re}.".format(ex=len(unwrap_spec), re=len(args)))
            unwrapped_args = ()
            for t, arg in zip(unwrap_spec, args):
                if t is int:
                    unwrapped_args += (arg.value,)
                else:
                    unwrapped_args += (arg,)
            result = func(*unwrapped_args)
            if wrap_spec is int:
                return space.newint(result)
            return result

        unwrapper.__qualname__ = name
        all_primitives.append(unwrapper)
        registry['$' + name] = len(all_primitives) - 1
        return None

    return expose


def get_index_of_primitive_named(name):
    return registry[name]


def get_number_of_arguments_of_primitive(idx):
    return primitive_number_of_arguments[idx]


@primitive('int_add', [int, int], int)
def simple_int_add(a, b):
    return a + b


@primitive('int_eq', [int, int], int)
def simple_int_eq(a, b):
    return a == b


# Syntactic Sugar Primitives
@primitive("int_sub", [int, int], int)
def simple_int_subtract(a, b):
    return a - b


@primitive("int_mul", [int, int], int)
def simple_int_multiply(a, b):
    return a * b


@primitive("int_div", [int, int], int)
def simple_int_divide(a, b):
    return a // b


@primitive("int_mod", [int, int], int)
def simple_int_modulo(a, b):
    return a % b


@primitive("int_inc", [int], int)
def simple_int_increment(a):
    return a + 1
