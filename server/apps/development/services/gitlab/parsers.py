# -*- coding: utf-8 -*-

from datetime import date, datetime
from typing import Optional

from django.utils.timezone import make_aware

GITLAB_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
GITLAB_DATE_FORMAT = '%Y-%m-%d'
STATE_MERGED = 'merged'


def parse_gl_datetime(value: str) -> Optional[datetime]:
    if not value:
        return None

    return make_aware(datetime.strptime(value, GITLAB_DATETIME_FORMAT))


def parse_gl_date(value: str) -> Optional[date]:
    if not value:
        return None

    return make_aware(datetime.strptime(value, GITLAB_DATE_FORMAT)).date()


def parse_state_merged(states: list) -> bool:
    if not states:
        return False

    return any(item.get('state') == STATE_MERGED for item in states)
