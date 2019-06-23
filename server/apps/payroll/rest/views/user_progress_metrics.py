from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rest_framework import permissions, serializers
from rest_framework.response import Response

from apps.core.rest.views import BaseGenericAPIView
from apps.core.utils.rest import parse_query_params
from apps.payroll.rest.permissions import CanViewUserMetrics
from apps.payroll.rest.serializers import UserProgressMetricsSerializer
from apps.payroll.services.metrics.progress.user import calculate_user_progress_metrics

User = get_user_model()


class UserProgressMetricsParamsSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()
    group = serializers.CharField()


class UserProgressMetricsView(BaseGenericAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        CanViewUserMetrics
    )

    @cached_property
    def user(self) -> User:
        user = get_object_or_404(
            User.objects,
            pk=self.kwargs['user_pk']
        )
        self.check_object_permissions(
            self.request,
            user
        )

        return user

    def get(self, request, **kwargs):
        params = parse_query_params(
            request,
            UserProgressMetricsParamsSerializer
        )

        metrics = calculate_user_progress_metrics(
            self.user,
            params['start'],
            params['end'],
            params['group']
        )

        return Response(UserProgressMetricsSerializer(
            metrics,
            many=True
        ).data)
