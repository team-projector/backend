from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet

from apps.development.services.team_members import filter_by_roles
from apps.users.models import User


def filter_allowed_for_user(queryset: QuerySet,
                            user: User) -> QuerySet:
    from apps.development.models import TeamMember

    allowed_users = {user}

    members = filter_by_roles(
        TeamMember.objects.filter(user=user),
        [
            TeamMember.roles.leader,
            TeamMember.roles.watcher,
        ],
    ).values_list(
        'team__members',
        flat=True,
    )

    for member in members:
        allowed_users.add(member)

    return queryset.filter(
        user__in=allowed_users,
    )


def check_allow_project_manager(user: User) -> None:
    if not user.roles.project_manager:
        raise PermissionDenied(
            'Only project managers can view project resources',
        )
