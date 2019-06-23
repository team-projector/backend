from rest_framework import permissions

from apps.payroll.services.users import is_teamleader_for_user


class CanManageWorkbreaks(permissions.BasePermission):
    message = 'You can\'t manage user workbreaks'

    def has_object_permission(self,
                              request,
                              view,
                              workbreak):
        if workbreak.user == request.user:
            return True

        return is_teamleader_for_user(
            request.user,
            workbreak.user
        )
