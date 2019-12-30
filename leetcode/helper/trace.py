import logging
from decorator import decorate


def _trace(f, *args, **kw):
    logger = logging.getLogger(f.__module__)
    kwstr = ', '.join('%r: %r' % (k, kw[k]) for k in sorted(kw))
    logger.info("calling %s:%s with args %s, {%s}" % (f.__name__, f.__code__.co_firstlineno, args, kwstr))
    ret = f(*args, **kw)
    logger.info("return %s:%s {%s}" % (f.__name__, f.__code__.co_firstlineno, ret))
    return ret


def trace(f):
    return decorate(f, _trace)
