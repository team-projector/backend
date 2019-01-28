import re
from datetime import date, datetime, timedelta
from typing import Optional, Pattern

from django.utils.timezone import make_aware

GITLAB_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
GITLAB_DATE_FORMAT = '%Y-%m-%d'
GITLAB_SPEND_TIMEDELTA_MAP = {
    'w': 'weeks',
    'd': 'days',
    'h': 'hours',
    'm': 'minutes',
    's': 'seconds',
}

RE_SPEND_PART: Pattern = re.compile(r'(?P<value>\d+)(?P<part>[wdhms])')


def parse_datetime(s: str) -> Optional[datetime]:
    if not s:
        return None

    return make_aware(datetime.strptime(s, GITLAB_DATETIME_FORMAT))


def parse_date(s: str) -> Optional[date]:
    if not s:
        return None

    return make_aware(datetime.strptime(s, GITLAB_DATE_FORMAT)).date()


def parse_spend(s: str) -> int:
    s = s or ''
    s = s.strip()

    if not s:
        return 0

    kwargs = {}

    for part in s.split(' '):
        m = RE_SPEND_PART.match(part)
        if not m:
            continue

        kwargs[GITLAB_SPEND_TIMEDELTA_MAP[m.group('part')]] = int(m.group('value'))

    return int(timedelta(**kwargs).total_seconds())
