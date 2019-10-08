# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from rest_framework.generics import get_object_or_404

from apps.users.services import user as user_service
from apps.users.services.allowed.user_progress_metrics import (
    filter_allowed_for_user,
)


def resolve_user_progress_metrics(parent, info, **kwargs):
    """Resolve progress metrics for user."""
    user = get_object_or_404(
        filter_allowed_for_user(
            get_user_model().objects.all(), info.context.user,
        ),
        pk=kwargs['user'],
    )

    return user_service.get_progress_metrics(
        user,
        kwargs['start'],
        kwargs['end'],
        kwargs['group'],
    )
