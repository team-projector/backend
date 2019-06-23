from rest_framework import permissions

from apps.payroll.services.users import is_teamleader_for_user


class CanApproveDeclineWorkbreaks(permissions.BasePermission):
    message = 'You can\'t approve or decline user workbreaks'

    def has_object_permission(self, request, view, workbreak):
        return is_teamleader_for_user(
            request.user,
            workbreak.user
        )
