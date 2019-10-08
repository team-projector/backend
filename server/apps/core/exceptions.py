# -*- coding: utf-8 -*-


class AppException(Exception):
    """Application exception."""

    def __init__(self, message=None):
        self.message = message
