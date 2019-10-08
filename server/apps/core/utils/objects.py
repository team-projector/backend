# -*- coding: utf-8 -*-

from functools import reduce
from typing import Any, Dict


def deep_getattr(obj: object, attr: str, default: Any = None) -> Any:
    try:
        return reduce(getattr, attr.split('.'), obj)
    except AttributeError:
        return default


class ObjectView:
    """Object view."""

    def __init__(self, dictionary: Dict):
        self.__dict__ = dictionary


def dict2obj(dictionary: Dict) -> object:
    return ObjectView(dictionary)
