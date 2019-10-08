# -*- coding: utf-8 -*-

from typing import Any, Tuple

from django.db import models
from django.utils import timezone


class ProjectManager(models.Manager):
    """The project manager."""

    def sync_gitlab(self, gl_id, **kwargs) -> Tuple[Any, bool]:
        """Save project by Gitlab id."""
        kwargs['gl_last_sync'] = timezone.now()

        return self.update_or_create(
            gl_id=gl_id,
            defaults=kwargs,
        )
