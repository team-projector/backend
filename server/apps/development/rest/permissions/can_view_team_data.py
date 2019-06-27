from django.db.models import Exists, OuterRef
from rest_framework import permissions

from apps.development.models import TeamMember
from apps.development.services.team_members import filter_by_roles


class CanViewTeamData(permissions.BasePermission):
    message = 'You can\'t view team data'

    def has_object_permission(self, request, view, team):
        allowed_member = filter_by_roles(TeamMember.objects.filter(
            team_id=OuterRef('team_id'),
            user=request.user
        ),
            [TeamMember.roles.leader, TeamMember.roles.watcher]
        )

        return team.members.annotate(
            is_allowed=Exists(allowed_member)
        ).filter(
            is_allowed=True
        ).exists()
