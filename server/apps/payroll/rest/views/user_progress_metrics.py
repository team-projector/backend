from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.response import Response

from apps.core.rest.views import BaseGenericAPIView
from apps.core.utils.rest import parse_query_params
from apps.payroll.rest.permissions import CanViewUserMetrics
from apps.payroll.rest.serializers import UserProgressMetricsSerializer
from apps.payroll.services.metrics.progress.user import (
    get_user_progress_metrics
)

User = get_user_model()


class UserProgressMetricsParamsSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()
    group = serializers.CharField()


class UserProgressMetricsView(BaseGenericAPIView):
    permission_classes = (
        CanViewUserMetrics,
    )

    queryset = User.objects.all()
    lookup_url_kwarg = 'user_pk'

    def get(self, request, **kwargs):
        params = parse_query_params(
            request,
            UserProgressMetricsParamsSerializer
        )

        metrics = get_user_progress_metrics(
            self.get_object(),
            params['start'],
            params['end'],
            params['group']
        )

        return Response(UserProgressMetricsSerializer(
            metrics,
            many=True
        ).data)
