from django.db.models import QuerySet

from apps.development.models import TeamMember
from apps.development.services.team_members import filter_by_roles
from apps.users.models import User


def filter_allowed_for_user(queryset: QuerySet, user: User) -> QuerySet:
    """Get spent time for user."""
    users = filter_by_roles(
        TeamMember.objects.filter(user=user),
        [TeamMember.roles.LEADER, TeamMember.roles.WATCHER],
    ).values_list("team__members", flat=True)

    return queryset.filter(user__in={*users, user.id})
