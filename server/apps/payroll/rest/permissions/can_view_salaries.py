from django.db.models import Exists, OuterRef
from rest_framework import permissions

from apps.development.models import TeamMember


class CanViewSalaries(permissions.BasePermission):
    message = 'You can\'t view user salaries'

    def has_object_permission(self,
                              request,
                              view,
                              salary):
        if salary.user == request.user:
            return True

        user_team_leader = TeamMember.objects.filter(
            team_id=OuterRef('team_id'),
            roles=TeamMember.roles.leader,
            user=request.user
        )

        return salary.user.team_members.annotate(
            is_team_leader=Exists(user_team_leader)
        ).filter(
            is_team_leader=True
        ).exists()
