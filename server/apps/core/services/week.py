import calendar

from constance import config

WEEK_DAY_MAP = {  # noqa: WPS407
    0: calendar.SUNDAY,
    1: calendar.MONDAY,
}


def get_first_week_day() -> int:
    """Get first week day."""
    return WEEK_DAY_MAP.get(int(config.FIRST_WEEK_DAY))  # type: ignore
