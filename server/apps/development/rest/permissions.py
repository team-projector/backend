from django.db.models import Exists, OuterRef
from rest_framework import permissions

from apps.development.models import TeamMember


class IsProjectManager(permissions.BasePermission):
    message = 'You can\'t view project manager resources'

    def has_permission(self, request, view):
        project_manager = TeamMember.objects.filter(
            team_id=OuterRef('team_id'),
            roles=TeamMember.roles.project_manager,
            user=request.user
        )

        return request.user.team_members \
            .annotate(is_pm=Exists(project_manager)) \
            .filter(is_pm=True).exists()
