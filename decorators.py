from functools import wraps
from timeit import default_timer as timer


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = timer()
        result = f(*args, **kw)
        te = timer()
        print('func:{!r} args:[{},{}] took: {:f} sec'.format(f.__name__, args, kw, te-ts))
        return result
    return wrap
