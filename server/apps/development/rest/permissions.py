from django.db.models import Exists, OuterRef
from rest_framework import permissions

from apps.development.models import TeamMember


class IsProjectManager(permissions.BasePermission):
    message = 'Only project managers can view project resources'

    def has_permission(self, request, view):
        return request.user.roles.project_manager


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


class CanSpendTime(permissions.BasePermission):
    message = 'You can\'t spend time'

    def has_object_permission(self, request, view, issue):
        if issue.user == request.user:
            return True
