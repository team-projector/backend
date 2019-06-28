from django.db.models import OuterRef, Exists
from rest_framework import filters

from apps.development.models import TeamMember
from apps.development.services.team_members import filter_by_roles


class AllowedSpentFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user_team_leader = filter_by_roles(TeamMember.objects.filter(
            team_id=OuterRef('team_id'),
            user=request.user
        ),
            [TeamMember.roles.leader, TeamMember.roles.watcher]
        )

        is_team_leader = request.user.team_members.annotate(
            is_team_leader=Exists(user_team_leader)
        ).filter(
            is_team_leader=True
        ).exists()

        if not is_team_leader:
            queryset = queryset.filter(user=request.user)

        return queryset
