from rest_framework import filters

from apps.core.utils.rest import parse_query_params
from apps.development.models import TeamMember
from apps.development.rest.filters.serializers import TeamParamsSerializer


class IssueTeamFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = parse_query_params(request, TeamParamsSerializer)

        team = params.get('team')

        if team:
            users = TeamMember.objects.get_no_watchers(team)
            queryset = queryset.filter(user__in=users)

        return queryset
