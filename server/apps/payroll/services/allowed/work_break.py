# -*- coding: utf-8 -*-

from django.core.exceptions import PermissionDenied

from apps.development.models import Team, TeamMember
from apps.development.services.team_members import filter_by_roles
from apps.users.models import User


def filter_allowed_for_user(self, user):
    users = TeamMember.objects.filter(
        user=user,
        roles=TeamMember.roles.leader,
    ).values_list(
        'team__members',
        flat=True,
    )

    return self.filter(
        user__in=(*users, user.id),
    )


def check_allow_filtering_by_team(team: Team,
                                  user: User) -> None:
    members = TeamMember.objects.filter(
        team=team,
        user=user,
    )

    allowed_members = filter_by_roles(
        members,
        [
            TeamMember.roles.leader,
            TeamMember.roles.watcher,
        ],
    ).exists()

    if not allowed_members:
        raise PermissionDenied("You can't filter by team")
