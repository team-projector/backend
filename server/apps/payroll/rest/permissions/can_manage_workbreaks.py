from rest_framework import permissions

from apps.development.models import TeamMember
from apps.payroll.services.users import user_related_with_another_by_roles


class CanManageWorkbreaks(permissions.BasePermission):
    message = 'You can\'t manage user workbreaks'

    def has_object_permission(self,
                              request,
                              view,
                              workbreak):
        if workbreak.user == request.user:
            return True

        return user_related_with_another_by_roles(
            request.user,
            workbreak.user,
            [TeamMember.roles.leader]
        )
