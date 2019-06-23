from django.db.models import Exists, OuterRef
from rest_framework import permissions

from apps.development.models import TeamMember


class IsTeamLeader(permissions.BasePermission):
    message = 'Only team leader can view team resources'

    def has_permission(self, request, view):
        return request.user.roles.team_leader

    def has_object_permission(self, request, view, team):
        team_leader = TeamMember.objects.filter(
            team_id=OuterRef('team_id'),
            roles=TeamMember.roles.leader,
            user=request.user
        )

        return team.members.annotate(
            is_team_leader=Exists(team_leader)
        ).filter(
            is_team_leader=True
        ).exists()
