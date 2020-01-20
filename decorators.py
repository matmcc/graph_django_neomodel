import logging
import pickle
from functools import wraps
from timeit import default_timer as timer

logger = logging.getLogger(__name__)


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = timer()
        result = f(*args, **kw)
        te = timer()
        print('func:{!r} took: {:f} sec'.format(f.__name__, te-ts))
        return result
    return wrap


def timing_args(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = timer()
        result = f(*args, **kw)
        te = timer()
        print('func:{!r} args:[{},{}] took: {:f} sec'.format(f.__name__, args, kw, te-ts))
        return result
    return wrap


def cache_result(f, path):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            with open(path, 'rb') as f_in:
                result = pickle.load(f_in)
                return result
        except FileNotFoundError:
            result = f(*args, **kwargs)
            with open(path, 'wb') as f_out:
                pickle.dump(result, f_out, protocol=pickle.HIGHEST_PROTOCOL)
            return result
    return wrap
