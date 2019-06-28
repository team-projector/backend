from rest_framework import permissions

from apps.development.models import TeamMember
from apps.payroll.services.users import user_related_with_another_by_team_roles


class CanViewUserMetrics(permissions.BasePermission):
    message = 'You can\'t view user metrics'

    def has_object_permission(self, request, view, user):
        if user == request.user:
            return True

        return user_related_with_another_by_team_roles(
            request.user,
            user,
            [TeamMember.roles.leader, TeamMember.roles.watcher]
        )
