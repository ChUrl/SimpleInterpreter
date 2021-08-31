def mark(w_context):
    w_context.mark = True

    if not hasattr(w_context, "slots"):  # skip primitive objects
        return

    for name, obj in w_context.slots.items():
        if name != "__parent__":  # only descent
            mark(obj)


def sweep(objects):
    objects[:] = filter(lambda obj: obj.mark, objects)  # inplace


def clear_marks(objects):
    for obj in objects:
        obj.mark = False
