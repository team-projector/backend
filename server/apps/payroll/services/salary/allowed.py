from django.db.models import QuerySet
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models import Team, TeamMember
from apps.development.services.team_members.filters import filter_by_roles
from apps.users.models import User


def filter_allowed_for_user(queryset: QuerySet, user: User) -> QuerySet:
    """Get salaries for user."""
    users = filter_by_roles(
        TeamMember.objects.filter(user=user),
        [TeamMember.roles.LEADER],
    ).values_list("team__members", flat=True)

    return queryset.filter(user__in={*users, user.id})


def check_allowed_filtering_by_team(team: Team, user: User) -> None:
    """Check whether user can get salaries by team."""
    queryset = TeamMember.objects.filter(team=team, user=user)

    can_filter = filter_by_roles(
        queryset,
        [TeamMember.roles.LEADER, TeamMember.roles.WATCHER],
    ).exists()

    if not can_filter:
        raise GraphQLPermissionDenied()
