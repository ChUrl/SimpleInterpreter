def mark(w_context):
    if w_context.mark:  # skip cycles
        return

    w_context.mark = True

    if not hasattr(w_context, "slots"):  # skip primitive objects
        return

    for name, obj in w_context.slots.items():
        mark(obj)


def sweep(objects):
    objects[:] = filter(lambda obj: obj.mark, objects)  # inplace


def clear_marks(objects):
    for obj in objects:
        obj.mark = False
