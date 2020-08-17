# -*- coding: utf-8 -*-

import typing

T = typing.TypeVar("T")  # noqa: WPS111


def sub_list(
    source: typing.Sequence[T], indexes: typing.Iterable[int],
) -> typing.List[T]:
    """
    Sub list.

    :param source:
    :type source: [T]
    :param indexes:
    :type indexes: [int]
    :rtype: [T]
    """
    return [source[index] for index in indexes]
