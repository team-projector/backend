# -*- coding: utf-8 -*-

from django.db.models import QuerySet

from apps.users.models import User


def filter_allowed_for_user(
    queryset: QuerySet,
    user: User,
) -> QuerySet:
    """Get allowed teams for user."""
    return queryset.filter(
        members=user,
    )
