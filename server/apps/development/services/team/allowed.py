# -*- coding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet

from apps.development.models import Team, TeamMember
from apps.development.services.team_members import filter_by_roles
from apps.users.models import User


def filter_allowed_for_user(
    queryset: QuerySet,
    user: User,
) -> QuerySet:
    """Get allowed teams for user."""
    return queryset.filter(
        members=user,
    )


def check_allow_get_metrics_by_user(
    team: Team,
    user: User,
) -> None:
    """Whether user allowed to get metrics."""
    can_filter = filter_by_roles(TeamMember.objects.filter(
        team=team,
        user=user,
    ),
        [TeamMember.roles.leader, TeamMember.roles.watcher],
    ).exists()

    if not can_filter:
        raise PermissionDenied