from django.core.exceptions import PermissionDenied

from apps.users.models import User


def check_project_manager(user: User) -> None:
    if not user.roles.project_manager:
        raise PermissionDenied(
            'Only project managers can view ticket metrics'
        )
