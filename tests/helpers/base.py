# -*- coding: utf-8 -*-

import datetime

from django.forms.models import model_to_dict


def model_to_dict_form(data: dict) -> dict:
    def replace(value):
        return "" if value is None else value

    original = model_to_dict(data)
    return {key: replace(value) for key, value in original.items()}


def format_date(date: datetime) -> str:
    return date.strftime("%Y-%m-%d")
