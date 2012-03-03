def task(f):
    f.__pub_task__ = True
    return f
