from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from rest_framework import permissions

from apps.development.models import TeamMember


User = get_user_model()


class CanViewUserMetrics(permissions.BasePermission):
    message = 'You can\'t view user metrics'

    def has_object_permission(self, request, view, user):
        if user == request.user:
            return True

        user_team_leader = TeamMember.objects.filter(
            team_id=OuterRef('team_id'),
            roles=TeamMember.roles.leader,
            user=request.user
        )

        return user.team_members.annotate(
            is_team_leader=Exists(user_team_leader)
        ).filter(
            is_team_leader=True
        ).exists()


class CanViewTeamMetrics(permissions.BasePermission):
    message = 'You can\'t view team metrics'

    def has_object_permission(self, request, view, team):
        user_team_leader = TeamMember.objects.filter(
            team_id=OuterRef('team_id'),
            roles=TeamMember.roles.leader,
            user=request.user
        )

        return team.members.annotate(
            is_team_leader=Exists(user_team_leader)
        ).filter(
            is_team_leader=True
        ).exists()


class CanViewEmbeddedUserMetrics(CanViewUserMetrics):
    def has_object_permission(self, request, view, user):
        show_metrics = request.query_params.get('metrics', 'false') != 'false'
        if not show_metrics:
            return True

        return super().has_object_permission(request, view, user)


class CanManageWorkbreaks(permissions.BasePermission):
    message = 'You can\'t manage user workbreaks'

    def has_object_permission(self, request, view, workbreak):
        if workbreak.user == request.user:
            return True

        return is_user_teamlead(request, workbreak.user)


class CanApproveDeclineWorkbreaks(permissions.BasePermission):
    message = 'You can\'t approve or decline user workbreaks'

    def has_object_permission(self, request, view, workbreak):
        return is_user_teamlead(request, workbreak.user)


def is_user_teamlead(request, user):
    teams = TeamMember.objects.filter(user=request.user,
                                      roles=TeamMember.roles.leader).values_list('team', flat=True)

    return User.objects.filter(team_members__team__in=teams,
                               team_members__roles=TeamMember.roles.developer,
                               id=user.id).exists()
