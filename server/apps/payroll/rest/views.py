from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions
from rest_framework.response import Response

from apps.core.rest.views import BaseGenericAPIView
from apps.core.utils.rest import parse_query_params
from apps.payroll.rest.permissions import CanViewUserMetrics
from .serializers import TimeExpenseSerializer, UserMetricSerializer, UserMetricsParamsSerializer
from ..models import SpentTime
from ..utils.metrics.user import create_calculator

User = get_user_model()


class UserMetricsView(BaseGenericAPIView):
    permission_classes = (permissions.IsAuthenticated, CanViewUserMetrics)

    @cached_property
    def user(self):
        user = get_object_or_404(User.objects, pk=self.kwargs['user_pk'])
        self.check_object_permissions(self.request, user)

        return user

    def get(self, request, **kwargs):
        params = parse_query_params(request, UserMetricsParamsSerializer)

        calculator = create_calculator(self.user, params['start'], params['end'], params['group'])
        metrics = calculator.calculate()

        return Response(UserMetricSerializer(metrics, many=True).data)


class TimeExpensesView(mixins.ListModelMixin,
                       BaseGenericAPIView):
    queryset = SpentTime.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('date',)
    permission_classes = (permissions.IsAuthenticated, CanViewUserMetrics)
    serializer_class = TimeExpenseSerializer

    @cached_property
    def user(self):
        user = get_object_or_404(User.objects, pk=self.kwargs['user_pk'])
        self.check_object_permissions(self.request, user)

        return user

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(user=self.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
