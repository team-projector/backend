# -*- coding: utf-8 -*-

from typing import Tuple

from django.db import models
from django.utils import timezone


class ProjectManager(models.Manager):
    """The project manager."""

    def update_from_gitlab(self, gl_id, **kwargs) -> Tuple[models.Model, bool]:
        """Save project by Gitlab id."""
        kwargs['gl_last_sync'] = timezone.now()

        return self.update_or_create(
            gl_id=gl_id,
            defaults=kwargs,
        )

    def for_sync(self) -> models.QuerySet:
        """Get projects for full sync with gitlab."""
        return self.filter(is_active=True)
