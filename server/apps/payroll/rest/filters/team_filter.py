from rest_framework import filters

from apps.core.utils.rest import parse_query_params
from apps.development.rest.filters.serializers import TeamParamsSerializer


class TeamFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = parse_query_params(request, TeamParamsSerializer)

        team = params.get('team')

        if team:
            queryset = queryset.filter(user__teams=team)

        return queryset
