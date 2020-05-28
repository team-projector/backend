# -*- coding: utf-8 -*-

import calendar

from decouple import config

TP_WEEKENDS_DAYS = (calendar.SATURDAY, calendar.SUNDAY)
TP_SYSTEM_USER_LOGIN = "system"
TP_APP_VERSION = config("APP_VERSION", default=None)
