# -*- coding: utf-8 -*-

from apps.core.consts import (
    SECONDS_PER_DAY,
    SECONDS_PER_HOUR,
    SECONDS_PER_MINUTE,
    SECONDS_PER_MONTH,
    SECONDS_PER_WEEK,
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
    """Get Gitlab durations."""
    durations = []

    for name, count in GITLAB_TIME_INTERVALS:
        duration = seconds // count
        if duration:
            seconds -= duration * count
            durations.append(f'{duration}{name}')

    return ''.join(durations)
