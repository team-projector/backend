from django.db.models import QuerySet

from apps.development.models import TeamMember
from apps.development.services.team_members import filter_by_roles
from apps.users.models import User


def filter_allowed_for_user(queryset: QuerySet,
                            user: User) -> QuerySet:
    allowed_users = filter_by_roles(
        TeamMember.objects.filter(user=user),
        [
            TeamMember.roles.leader,
            TeamMember.roles.watcher
        ]
    ).values_list(
        'team__members',
        flat=True
    )

    return queryset.filter(id__in={*allowed_users, user.id})
