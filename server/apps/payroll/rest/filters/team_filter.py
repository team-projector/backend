from rest_framework import filters, serializers

from apps.core.utils.rest import parse_query_params


class ParamsSerializer(serializers.Serializer):
    team = serializers.IntegerField(required=False)


class TeamFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = parse_query_params(request, ParamsSerializer)

        team_id = params.get('team')

        if team_id:
            queryset = queryset.filter(user__teams=team_id)

        return queryset
