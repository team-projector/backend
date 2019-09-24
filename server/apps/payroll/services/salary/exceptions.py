# -*- coding: utf-8 -*-

from apps.core.exceptions import AppException


class EmptySalaryException(AppException):
    def __init__(self):
        pass
