# -*- coding: utf-8 -*-

from typing import Tuple

from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

from apps.users.models import User


class MergeRequestManager(models.Manager):
    """The merge request model manager."""

    def update_from_gitlab(self, gl_id, **kwargs) -> Tuple[models.Model, bool]:
        """Save merge request by Gitlab id."""
        kwargs['gl_last_sync'] = timezone.now()

        return self.update_or_create(
            gl_id=gl_id,
            defaults=kwargs,
        )

    def allowed_for_user(self, user: User) -> QuerySet:
        """Issues allowed for team leader and watchers."""
        from apps.development.services.merge_request.allowed import (  # noqa: WPS433, E501
            filter_allowed_for_user,
        )

        return filter_allowed_for_user(self, user)
