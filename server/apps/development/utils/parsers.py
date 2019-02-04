from datetime import date, datetime
from typing import Optional

from django.utils.timezone import make_aware

GITLAB_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
GITLAB_DATE_FORMAT = '%Y-%m-%d'


def parse_gl_datetime(s: str) -> Optional[datetime]:
    if not s:
        return None

    return make_aware(datetime.strptime(s, GITLAB_DATETIME_FORMAT))


def parse_gl_date(s: str) -> Optional[date]:
    if not s:
        return None

    return make_aware(datetime.strptime(s, GITLAB_DATE_FORMAT)).date()


def parse_date(s: str, fmt='%Y-%m-%d') -> Optional[date]:
    if not s:
        return None

    return datetime.strptime(s, fmt).date()
