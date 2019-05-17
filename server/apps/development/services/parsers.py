from datetime import date, datetime
from typing import Optional

GITLAB_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
GITLAB_DATE_FORMAT = '%Y-%m-%d'


def parse_date(s: str, fmt='%Y-%m-%d') -> Optional[date]:
    if not s:
        return None

    return datetime.strptime(s, fmt).date()
