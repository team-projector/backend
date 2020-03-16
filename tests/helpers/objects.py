# -*- coding: utf-8 -*-


class AttrDict(dict):  # delete
    def __init__(self, *args, **kwargs):
        """Initializing."""
        super().__init__(*args, **kwargs)
        self.__dict__ = self
