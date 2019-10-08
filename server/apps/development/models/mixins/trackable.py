# -*- coding: utf-8 -*-

from apps.development.models.mixins import NotableMixin
from apps.payroll.models.mixins import SpentTimesMixin


class TrackableMixin(
    NotableMixin,
    SpentTimesMixin,
):
    """Mixin for trackable entities."""

    class Meta:
        abstract = True
