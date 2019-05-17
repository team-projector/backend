from django.db.models import Exists, OuterRef
from rest_framework import permissions

from apps.development.models import TeamMember


class CanViewUserMetrics(permissions.BasePermission):
    message = 'You can\'t view user metrics'

    def has_object_permission(self, request, view, user):
        if user == request.user:
            return True

        user_team_leader = TeamMember.objects.filter(team_id=OuterRef('team_id'),
                                                     roles=TeamMember.roles.leader,
                                                     user=request.user)

        return user.team_members \
            .annotate(is_team_leader=Exists(user_team_leader)) \
            .filter(is_team_leader=True).exists()


class CanViewEmbeddedUserMetrics(CanViewUserMetrics):
    def has_object_permission(self, request, view, user):
        show_metrics = request.query_params.get('metrics', 'false') != 'false'
        if not show_metrics:
            return True

        return super().has_object_permission(request, view, user)


class CanManageWorkbeaks(permissions.BasePermission):
    message = 'You can\'t manage user workbreaks'

    def has_object_permission(self, request, view, workbreak):
        if workbreak.user == request.user:
            return True

        return is_user_teamlead(request)


class CanApproveDeclineWorkbeaks(permissions.BasePermission):
    message = 'You can\'t approve or decline user workbreaks'

    def has_object_permission(self, request, view, workbreak):
        return is_user_teamlead(request)


def is_user_teamlead(request):
    team_leader = TeamMember.objects.filter(team_id=OuterRef('team_id'),
                                            roles=TeamMember.roles.leader,
                                            user=request.user)

    return request.user.team_members \
        .annotate(is_team_leader=Exists(team_leader)) \
        .filter(is_team_leader=True).exists()
