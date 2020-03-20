# -*- coding: utf-8 -*-

from collections import Iterable, Sequence
from typing import List, TypeVar

T = TypeVar("T")  # noqa: WPS111


def sub_list(source: Sequence[T], indexes: Iterable[int]) -> List[T]:
    return [source[index] for index in indexes]
