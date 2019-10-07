# -*- coding: utf-8 -*-

from django.db.models import F


class NullsAlwaysLastOrderingMixin:
    """Nulls always last odering mixin."""

    def get_ordering_value(self, param):
        """Get ordering value."""
        ord_value = super().get_ordering_value(param)  # type: ignore

        descending = ord_value.startswith('-')
        value = ord_value[1:] if descending else ord_value

        if descending:
            return F(value).desc(nulls_last=True)

        return F(value).asc(nulls_last=True)
