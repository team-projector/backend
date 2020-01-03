# -*- coding: utf-8 -*-

from django.db import models
from django_filters import OrderingFilter


class NullsAlwaysLastOrderingMixin(OrderingFilter):
    """Nulls always last odering mixin."""

    def get_ordering_value(self, choice):
        """Get ordering value."""
        ord_value = super().get_ordering_value(choice)

        descending = ord_value.startswith("-")
        normalized_value = ord_value[1:] if descending else ord_value

        if descending:
            return models.F(normalized_value).desc(nulls_last=True)

        return models.F(normalized_value).asc(nulls_last=True)
