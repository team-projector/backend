# -*- coding: utf-8 -*-

from apps.core.gitlab.parsers import GITLAB_DATE_FORMAT, GITLAB_DATETIME_FORMAT


def gl_format_date(date):
    """
    Gl format date.

    :param date:
    """
    return str(date.strftime(GITLAB_DATE_FORMAT))


def gl_format_datetime(dt):
    """
    Gl format datetime.

    :param dt:
    """
    return str(dt.strftime(GITLAB_DATETIME_FORMAT))
