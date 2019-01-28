from functools import reduce


def deep_getattr(obj, attr, default=None):
    try:
        return reduce(getattr, attr.split('.'), obj)
    except AttributeError:
        return default


def dict2obj(d) -> object:
    return objectview(d)


class objectview:
    def __init__(self, d):
        self.__dict__ = d
