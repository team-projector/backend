from rest_framework import permissions

from apps.development.models import TeamMember
from apps.payroll.services.users import user_related_with_another_by_team_roles


class CanApproveDeclineWorkbreaks(permissions.BasePermission):
    message = 'You can\'t approve or decline user workbreaks'

    def has_object_permission(self, request, view, workbreak):
        return user_related_with_another_by_team_roles(
            request.user,
            workbreak.user,
            [TeamMember.roles.leader]
        )
