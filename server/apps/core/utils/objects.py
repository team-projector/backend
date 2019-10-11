# -*- coding: utf-8 -*-

from functools import reduce
from typing import Any, Dict


def deep_getattr(obj: object, attr: str, default: Any = None) -> Any:  # noqa WPS110
    """Get attribute from object."""
    try:
        return reduce(getattr, attr.split('.'), obj)
    except AttributeError:
        return default


class ObjectView:
    """Object view."""

    def __init__(self, dictionary: Dict):
        """Initialize self."""
        self.__dict__ = dictionary


def dict2obj(dictionary: Dict) -> object:
    """Create ObjectView from dictionary."""
    return ObjectView(dictionary)
