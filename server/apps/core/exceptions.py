# -*- coding: utf-8 -*-


class AppException(Exception):
    def __init__(self, message):
        self.message = message
