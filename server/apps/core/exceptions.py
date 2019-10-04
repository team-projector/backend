# -*- coding: utf-8 -*-


class AppException(Exception):
    """
    Application exception.
    """
    def __init__(self, message):
        self.message = message
