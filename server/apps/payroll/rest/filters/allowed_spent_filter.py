from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import filters

from apps.development.models import TeamMember

User = get_user_model()


class AllowedSpentFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        query = Q(user=request.user)
        query &= Q(
            Q(roles=TeamMember.roles.leader) | Q(roles=TeamMember.roles.watcher)
        )

        is_team_leader = TeamMember.objects.filter(query).exists()

        if not is_team_leader:
            queryset = queryset.filter(user=request.user)

        return queryset
