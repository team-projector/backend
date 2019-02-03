from datetime import date, datetime


def date2datetime(d: date) -> datetime:
    return datetime.combine(d, datetime.min.time())
