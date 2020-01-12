import logging
from functools import wraps
from timeit import default_timer as timer

logger = logging.getLogger(__name__)


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = timer()
        result = f(*args, **kw)
        te = timer()
        logger.info('func:{!r} took: {:f} sec'.format(f.__name__, te-ts))
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
