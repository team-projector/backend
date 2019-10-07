# -*- coding: utf-8 -*-

from django.db import models


class Timestamps(models.Model):
    """A mixin with created and updated fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
