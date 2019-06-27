from rest_framework import permissions

from apps.development.models import TeamMember, Team
from apps.development.services.team_members import filter_by_roles


class CanViewTeamData(permissions.BasePermission):
    message = 'You can\'t view team data'

    def has_object_permission(self, request, view, team: Team) -> bool:
        return filter_by_roles(TeamMember.objects.filter(
            team=team,
            user=request.user
        ),
            [TeamMember.roles.leader, TeamMember.roles.watcher]
        ).exists()
