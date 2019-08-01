from rest_framework.exceptions import ValidationError
from django.db.models import QuerySet

from apps.development.models import Team, TeamMember
from apps.development.services.team_members import filter_by_roles
from apps.users.models import User


def filter_allowed_for_user(queryset: QuerySet,
                            user: User) -> QuerySet:
    users = filter_by_roles(
        TeamMember.objects.filter(user=user),
        [
            TeamMember.roles.leader
        ]
    ).values_list(
        'team__members',
        flat=True
    )

    return queryset.filter(user__in={*users, user.id})


def check_allowed_filtering_by_team(team: Team,
                                    user: User) -> None:
    queryset = TeamMember.objects.filter(
        team=team,
        user=user
    )

    can_filtering = filter_by_roles(
        queryset,
        [
            TeamMember.roles.leader,
            TeamMember.roles.watcher
        ]
    ).exists()

    if not can_filtering:
        raise ValidationError('Can\'t filter by team')