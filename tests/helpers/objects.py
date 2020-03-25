# -*- coding: utf-8 -*-

from django.forms.models import model_to_dict


class AttrDict(dict):  # delete
    def __init__(self, *args, **kwargs):
        """Initializing."""
        super().__init__(*args, **kwargs)
        self.__dict__ = self


def model_to_dict_form(data: dict) -> dict:
    def replace(value):
        return "" if value is None else value

    original = model_to_dict(data)
    return {key: replace(value) for key, value in original.items()}
