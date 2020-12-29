from typing import Optional

from django.db.models import QuerySet
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models import Team, TeamMember
from apps.development.services.team_members.filters import filter_by_roles
from apps.users.models import User


def filter_allowed_for_user(
    queryset: QuerySet,
    user: Optional[User],
) -> QuerySet:
    """Get allowed teams for user."""
    if not user:
        return queryset.none()

    return queryset.filter(members=user)


def check_allow_get_metrics_by_user(team: Team, user: User) -> None:
    """Whether user allowed to get metrics."""
    can_filter = filter_by_roles(
        TeamMember.objects.filter(team=team, user=user),
        [TeamMember.roles.LEADER, TeamMember.roles.WATCHER],
    ).exists()

    if not can_filter:
        raise GraphQLPermissionDenied()
