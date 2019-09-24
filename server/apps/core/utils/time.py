# -*- coding: utf-8 -*-

from datetime import timedelta


def seconds(**kwargs):
    return timedelta(**kwargs).total_seconds()
