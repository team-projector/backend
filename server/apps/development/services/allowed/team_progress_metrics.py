from django.db.models import QuerySet

from apps.development.models import Team, TeamMember
from apps.development.services.team_members import filter_by_roles
from apps.users.models import User


def is_allowed_for_user(team: Team,
                        user: User) -> QuerySet:
    return filter_by_roles(TeamMember.objects.filter(
        team=team,
        user=user
    ),
        [TeamMember.roles.leader, TeamMember.roles.watcher]
    ).exists()