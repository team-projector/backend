# -*- coding: utf-8 -*-

from typing import Tuple

from django.db import models
from django.utils import timezone

from apps.users.models import User


class IssueManager(models.Manager):
    """The issue model manager."""

    def update_from_gitlab(self, gl_id, **kwargs) -> Tuple[models.Model, bool]:
        """Save issue by Gitlab id."""
        kwargs["gl_last_sync"] = timezone.now()

        return self.update_or_create(
            gl_id=gl_id,
            defaults=kwargs,
        )

    def allowed_for_user(self, user: User) -> models.QuerySet:
        """Issues allowed for team leader and watchers."""
        from apps.development.services.issue.allowed import (  # noqa: WPS433
            filter_allowed_for_user,
        )

        return filter_allowed_for_user(self, user)
