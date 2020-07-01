# -*- coding: utf-8 -*-

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _


class NotableMixin(models.Model):
    """Create notes when loading issues or merge requests."""

    class Meta:
        abstract = True

    notes = GenericRelation(
        "development.Note",
        verbose_name=_("VN__NOTES"),
        help_text=_("HT__NOTES"),
    )

    def __str__(self):
        """Returns object string representation."""
        return ""
