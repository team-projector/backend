# -*- coding: utf-8 -*-

from apps.core.consts import (
    SECONDS_PER_MONTH,
    SECONDS_PER_WEEK,
    SECONDS_PER_DAY,
    SECONDS_PER_HOUR,
    SECONDS_PER_MINUTE,
)

GITLAB_TIME_INTERVALS = (
    ('mo', SECONDS_PER_MONTH),
    ('w', SECONDS_PER_WEEK),
    ('d', SECONDS_PER_DAY),
    ('h', SECONDS_PER_HOUR),
    ('m', SECONDS_PER_MINUTE),
    ('s', 1),
)


def gl_duration(seconds: int) -> str:
    result = []

    for name, count in GITLAB_TIME_INTERVALS:
        value = seconds // count
        if value:
            seconds -= value * count
            result.append(f'{value}{name}')

    return ''.join(result)
