from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet

from apps.users.models import User


def filter_allowed_for_user(queryset: QuerySet,
                            user: User) -> QuerySet:
    if not user.roles.project_manager:
        raise PermissionDenied(
            'Only project managers can view project resources'
        )

    return queryset
