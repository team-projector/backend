from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.response import Response

from apps.core.rest.views import BaseGenericAPIView
from apps.core.utils.rest import parse_query_params
from .serializers import TimeExpenseSerializer, UserMetricSerializer, UserMetricsParamsSerializer
from ..models import SpentTime
from ..utils.metrics.user import create_calculator

User = get_user_model()


class UserMetricsView(BaseGenericAPIView):
    def get(self, request, user_pk):
        user = get_object_or_404(User.objects, pk=user_pk)
        params = parse_query_params(request, UserMetricsParamsSerializer)

        calculator = create_calculator(user, params['start'], params['end'], params['group'])
        metrics = calculator.calculate()

        return Response(UserMetricSerializer(metrics, many=True).data)


class TimeExpensesView(mixins.ListModelMixin,
                       BaseGenericAPIView):
    queryset = SpentTime.objects.all()
    filter_backends = (DjangoFilterBackend,)
    serializer_class = TimeExpenseSerializer
    filter_fields = ('date',)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        user = get_object_or_404(User.objects, pk=self.kwargs['user_pk'])
        return queryset.filter(user=user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
