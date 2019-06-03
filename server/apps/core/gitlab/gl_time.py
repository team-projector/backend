SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 60 * SECONDS_PER_MINUTE
SECONDS_PER_DAY = 24 * SECONDS_PER_HOUR
SECONDS_PER_WEEK = 7 * SECONDS_PER_DAY
SECONDS_PER_MONTH = 4 * SECONDS_PER_WEEK

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
