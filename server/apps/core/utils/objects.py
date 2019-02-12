from functools import reduce
from typing import Any, Dict


def deep_getattr(obj: object, attr: str, default: Any = None) -> Any:
    try:
        return reduce(getattr, attr.split('.'), obj)
    except AttributeError:
        return default


class ObjectView:
    def __init__(self, d: Dict):
        self.__dict__ = d


def dict2obj(d: Dict) -> object:
    return ObjectView(d)
