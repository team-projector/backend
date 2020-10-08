from datetime import date, datetime
from typing import Dict, List, Optional

from django.utils.timezone import make_aware

GITLAB_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"  # noqa: WPS323
GITLAB_DATE_FORMAT = "%Y-%m-%d"  # noqa: WPS323
STATE_MERGED = "merged"


def parse_gl_datetime(gl_datetime: str) -> Optional[datetime]:
    """Get a naive datetime.datetime from gitlab datetime."""
    if not gl_datetime:
        return None

    return make_aware(datetime.strptime(gl_datetime, GITLAB_DATETIME_FORMAT))


def parse_gl_date(gl_date: str) -> Optional[date]:
    """Get a naive datetime.datetime from gitlab date."""
    if not gl_date:
        return None

    return make_aware(datetime.strptime(gl_date, GITLAB_DATE_FORMAT)).date()


def parse_state_merged(states: List[Dict[str, str]]) -> bool:
    """Check whether state merged is exists."""
    if not states:
        return False

    return any(state.get("state") == STATE_MERGED for state in states)
