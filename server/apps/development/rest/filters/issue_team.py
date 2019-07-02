from rest_framework import filters, serializers

from apps.core.utils.rest import parse_query_params
from apps.development.models import Team, TeamMember


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
            """
            Filter by team members with roles not a watcher
            https://gitlab.com/junte/team-projector/backend/issues/168
            """
            users = TeamMember.objects.filter(
                team=team,
                roles=~TeamMember.roles.watcher
            ).values_list(
                'user',
                flat=True
            )
            queryset = queryset.filter(user__in=users)

        return queryset
