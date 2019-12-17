# -*- coding: utf-8 -*-

from typing import Tuple

from django.db import models
from django.utils import timezone


class MilestoneManager(models.Manager):
    """The merge request model manager."""

    def update_from_gitlab(
        self,
        gl_id,
        **kwargs,
    ) -> Tuple[models.Model, bool]:
        """Save milestone by Gitlab id."""
        kwargs['gl_last_sync'] = timezone.now()

        return self.update_or_create(
            gl_id=gl_id,
            defaults=kwargs,
        )
