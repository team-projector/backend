# -*- coding: utf-8 -*-

from typing import Any, Tuple

from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

from apps.users.models import User

from ...services.allowed.merge_requests import filter_allowed_for_user


class MergeRequestManager(models.Manager):
    """The merge request model manager."""

    def sync_gitlab(self, gl_id, **kwargs) -> Tuple[Any, bool]:
        """Save merge request by Gitlab id."""
        kwargs['gl_last_sync'] = timezone.now()

        return self.update_or_create(
            gl_id=gl_id,
            defaults=kwargs,
        )

    def allowed_for_user(self, user: User) -> QuerySet:
        """Issues allowed for team leader and watchers."""
        return filter_allowed_for_user(self, user)
