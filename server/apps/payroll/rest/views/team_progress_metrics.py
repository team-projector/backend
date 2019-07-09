from rest_framework import permissions, serializers
from rest_framework.response import Response

from apps.core.rest.views import BaseGenericAPIView
from apps.core.utils.rest import parse_query_params
from apps.development.models import Team
from apps.development.rest.permissions import CanViewTeamData
from apps.payroll.rest.serializers import TeamMemberProgressMetricsSerializer
from apps.payroll.services.metrics.progress.team import (
    get_team_progress_metrics
)


class TeamProgressMetricsParamsSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()
    group = serializers.CharField()


class TeamProgressMetricsView(BaseGenericAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        CanViewTeamData,
    )

    queryset = Team.objects.all()
    lookup_url_kwarg = 'team_pk'

    def get(self, request, **kwargs):
        params = parse_query_params(
            request,
            TeamProgressMetricsParamsSerializer
        )

        metrics = get_team_progress_metrics(
            self.get_object(),
            params['start'],
            params['end'],
            params['group']
        )

        return Response(TeamMemberProgressMetricsSerializer(
            metrics,
            many=True
        ).data)
