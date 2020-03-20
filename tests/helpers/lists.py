# -*- coding: utf-8 -*-

import typing

T = typing.TypeVar("T")  # noqa WPS111


def sub_list(
    source: typing.Sequence, indexes: typing.Iterable[int]
) -> typing.List[T]:
    return [source[index] for index in indexes]
