# -*- coding: utf-8 -*-

from datetime import date, datetime
from typing import Optional

from django.utils.timezone import make_aware

GITLAB_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
GITLAB_DATE_FORMAT = '%Y-%m-%d'
STATE_MERGED = 'merged'


def parse_gl_datetime(s: str) -> Optional[datetime]:
    if not s:
        return None

    return make_aware(datetime.strptime(s, GITLAB_DATETIME_FORMAT))


def parse_gl_date(s: str) -> Optional[date]:
    if not s:
        return None

    return make_aware(datetime.strptime(s, GITLAB_DATE_FORMAT)).date()


def parse_state_merged(l: list) -> bool:
    if not l:
        return False

    return any(item.get('state') == STATE_MERGED for item in l)
