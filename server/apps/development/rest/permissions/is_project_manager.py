from rest_framework import permissions


class IsProjectManager(permissions.BasePermission):
    message = 'Only project managers can view project resources'

    def has_permission(self, request, view):
        return request.user.roles.project_manager
