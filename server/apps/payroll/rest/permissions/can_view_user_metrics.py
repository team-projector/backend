from django.db.models import Exists, OuterRef
from rest_framework import permissions

from apps.development.models import TeamMember
from apps.development.services.team_members import filter_by_roles


class CanViewUserMetrics(permissions.BasePermission):
    message = 'You can\'t view user metrics'

    def has_object_permission(self, request, view, user):
        if user == request.user:
            return True

        user_team_leader = filter_by_roles(TeamMember.objects.filter(
            team_id=OuterRef('team_id'),
            user=request.user
        ),
            [TeamMember.roles.leader, TeamMember.roles.watcher]
        )

        return user.team_members.annotate(
            is_team_leader=Exists(user_team_leader)
        ).filter(
            is_team_leader=True
        ).exists()
