from datetime import date, datetime, timedelta


def date2datetime(d: date) -> datetime:
    return datetime.combine(d, datetime.min.time())


def next_weekday(d: date, weekday: int) -> date:
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7

    return d + timedelta(days_ahead)
