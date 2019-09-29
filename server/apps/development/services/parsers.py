# -*- coding: utf-8 -*-

from datetime import date, datetime
from typing import Optional

GITLAB_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
GITLAB_DATE_FORMAT = '%Y-%m-%d'


def parse_date(date_str: str, fmt='%Y-%m-%d') -> Optional[date]:
    if not date_str:
        return None

    return datetime.strptime(date_str, fmt).date()
