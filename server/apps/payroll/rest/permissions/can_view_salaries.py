from rest_framework import permissions

from apps.development.models import TeamMember
from apps.payroll.services.users import user_related_with_another_by_team_roles


class CanViewSalaries(permissions.BasePermission):
    message = 'You can\'t view user salaries'

    def has_object_permission(self,
                              request,
                              view,
                              salary):
        if salary.user == request.user:
            return True

        return user_related_with_another_by_team_roles(
            request.user,
            salary.user,
            [TeamMember.roles.leader]
        )
