# -*- coding: utf-8 -*-

from collections import OrderedDict

from django_filters import OrderingFilter
from graphene.utils import str_converters


class CamelCasedOrderingMixin(OrderingFilter):
    """
    Examples.

    ("user__due_date",) becomes => {"user__due_date": "user__dueDate"}
    (("due_date", "due_date"),) becomes => {"due_date": "dueDate"}
    {"due_date": "due_date"} becomes => {"due_date": "dueDate"}
    """

    @classmethod
    def normalize_fields(cls, fields):
        """Normalize fields."""
        ret = super().normalize_fields(fields)

        return OrderedDict(
            [
                (
                    key,
                    "__".join(
                        str_converters.to_camel_case(choice)
                        for choice in choice_field.split("__")
                    ),
                )
                for key, choice_field in ret.items()
            ],
        )
