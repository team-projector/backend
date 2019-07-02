from rest_framework import filters, serializers

from apps.core.utils.rest import parse_query_params
from apps.development.models import Team


class ParamsSerializer(serializers.Serializer):
    team = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        required=False
    )

    def validate_team(self, value):
        return value


class IssueTeamFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = parse_query_params(request, ParamsSerializer)

        team = params.get('team')

        if team:
            queryset = queryset.filter(user__teams=team)

        return queryset
