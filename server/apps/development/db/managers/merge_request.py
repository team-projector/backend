from typing import Any, Tuple

from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

from apps.development.services.allowed.merge_requests import \
    filter_allowed_for_user
from apps.users.models import User


class MergeRequestManager(models.Manager):
    def sync_gitlab(self, gl_id, **kwargs) -> Tuple[Any, bool]:
        kwargs['gl_last_sync'] = timezone.now()

        return self.update_or_create(
            gl_id=gl_id,
            defaults=kwargs
        )

    def allowed_for_user(self, user: User) -> QuerySet:
        return filter_allowed_for_user(self, user)
