# -*- coding: utf-8 -*-

from django_filters import OrderingFilter as BaseOrderingFilter

from .mixins import CamelCasedOrderingMixin, NullsAlwaysLastOrderingMixin


class OrderingFilter(
    CamelCasedOrderingMixin,
    NullsAlwaysLastOrderingMixin,
    BaseOrderingFilter,
):
    """Ordering filter."""
