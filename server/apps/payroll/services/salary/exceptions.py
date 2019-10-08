# -*- coding: utf-8 -*-

from apps.core.exceptions import AppException


class EmptySalaryException(AppException):
    """Exception if payrolls not locked."""
