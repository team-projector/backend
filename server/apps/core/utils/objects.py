from functools import reduce


def deep_getattr(obj, attr, default=None):
    try:
        return reduce(getattr, attr.split('.'), obj)
    except AttributeError:
        return default
