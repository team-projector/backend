from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rest_framework import permissions, serializers
from rest_framework.response import Response

from apps.core.rest.views import BaseGenericAPIView
from apps.core.utils.rest import parse_query_params
from apps.development.models import Team
from apps.development.rest.permissions import CanViewTeamData
from apps.payroll.rest.serializers import TeamMemberProgressMetricsSerializer
from apps.payroll.services.metrics.progress.team import (
    calculate_team_progress_metrics
)


class TeamProgressMetricsParamsSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()
    group = serializers.CharField()


class TeamProgressMetricsView(BaseGenericAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        CanViewTeamData
    )

    @cached_property
    def team(self) -> Team:
        team = get_object_or_404(
            Team.objects,
            pk=self.kwargs['team_pk']
        )
        self.check_object_permissions(
            self.request,
            team
        )

        return team

    def get(self, request, **kwargs):
        params = parse_query_params(
            request,
            TeamProgressMetricsParamsSerializer
        )

        metrics = calculate_team_progress_metrics(
            self.team,
            params['start'],
            params['end'],
            params['group']
        )

        return Response(TeamMemberProgressMetricsSerializer(
            metrics,
            many=True
        ).data)
