registry = {}
all_primitives = []
primitive_number_of_arguments = []


def primitive(name, unwrap_spec, wrap_spec):  # decorator arguments
    assert '$' + name not in registry, '${name} already defined'.format(name=name)
    primitive_number_of_arguments.append(len(unwrap_spec) - 1)  # first argument is the receiver

    def expose(func):  # decorator
        def unwrapper(w_receiver, args_w, space):
            args = [w_receiver] + args_w
            if len(args) != len(unwrap_spec):  # check that call args match primitive args
                raise TypeError(
                    "Expected {ex} arguments, received {re}.".format(ex=len(unwrap_spec), re=len(args)))

            unwrapped_args = ()
            for t, arg in zip(unwrap_spec, args):  # unpack values from simple-objects
                if t in [int, str, float]:  # Project: Double, String
                    unwrapped_args += (arg.value,)
                elif t is bool:  # Project: Boolean
                    unwrapped_args += (bool(arg.value),)  # isn't really necessary because "1 or 0" is also valid
                else:
                    unwrapped_args += (arg,)

            result = func(*unwrapped_args)  # actual call

            if wrap_spec is int:  # wrap the result
                return space.newint(result)
            elif wrap_spec is bool:  # Project: Boolean
                return space.newbool(result)
            elif wrap_spec is str:  # Project: String
                return space.newstring(result)
            elif wrap_spec is float:  # Project: Double
                return space.newdouble(result)
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


# Project: Sugar
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


# Project: Boolean, String, Double
@primitive("int_tobool", [int], bool)
def simple_int_tobool(a):
    return a


@primitive("int_tostr", [int], str)
def simple_int_tobstr(a):
    return a


@primitive("int_todouble", [int], float)
def simple_int_tobdouble(a):
    return a


# Project: Boolean
@primitive("bool_and", [bool, bool], bool)
def simple_bool_and(a, b):
    return a and b


@primitive("bool_or", [bool, bool], bool)
def simple_bool_or(a, b):
    return a or b


@primitive("bool_not", [bool], bool)
def simple_bool_not(a):
    return not a


@primitive("bool_toint", [bool], int)
def simple_bool_toint(a):
    return a


@primitive("bool_tostr", [bool], str)
def simple_bool_tostr(a):
    return str(a).lower()


@primitive("bool_todouble", [bool], float)
def simple_bool_todouble(a):
    return a


# bool stuff for int
@primitive("int_eq", [int, int], bool)
def simple_int_eq(a, b):
    return a == b


@primitive("int_leq", [int, int], bool)
def simple_int_leq(a, b):
    return a <= b


@primitive("int_geq", [int, int], bool)
def simple_int_geq(a, b):
    return a >= b


@primitive("int_greater", [int, int], bool)
def simple_int_greater(a, b):
    return a > b


@primitive("int_less", [int, int], bool)
def simple_int_less(a, b):
    return a < b


# Project: String
@primitive("str_eq", [str, str], bool)
def simple_str_eq(a, b):
    return a == b


@primitive("str_add", [str, str], str)
def simple_str_add(a, b):
    return a + b


@primitive("str_rev", [str], str)
def simple_str_eq(a):
    return a[::-1]


@primitive("str_len", [str], int)
def simple_str_eq(a):
    return len(a)


@primitive("str_toint", [str], int)
def simple_str_toint(a):
    return a


@primitive("str_tobool", [str], bool)
def simple_str_tobool(a):
    return a == "true"


@primitive("str_todouble", [str], float)
def simple_str_todouble(a):
    return a


# Project: Double
@primitive("double_eq", [float, float], bool)
def simple_double_eq(a, b):
    return a == b


@primitive("double_add", [float, float], float)
def simple_double_add(a, b):
    return a + b


@primitive("double_sub", [float, float], float)
def simple_double_sub(a, b):
    return a - b


@primitive("double_mul", [float, float], float)
def simple_double_mul(a, b):
    return a * b


@primitive("double_div", [float, float], float)
def simple_double_div(a, b):
    return a / b


@primitive("double_toint", [float], int)
def simple_double_toint(a):
    return a


@primitive("double_tobool", [float], bool)
def simple_double_tobool(a):
    return a


@primitive("double_tostr", [float], str)
def simple_double_tostr(a):
    return a
