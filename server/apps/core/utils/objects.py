# -*- coding: utf-8 -*-

from typing import Dict


class ObjectView:
    """Object view."""

    def __init__(self, dictionary: Dict[str, object]):
        """Initialize self."""
        self.__dict__ = dictionary


def dict2obj(dictionary: Dict[str, object]) -> ObjectView:
    """Create ObjectView from dictionary."""
    return ObjectView(dictionary)
