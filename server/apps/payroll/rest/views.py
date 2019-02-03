from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.response import Response

from apps.core.rest.views import BaseGenericAPIView, BaseGenericViewSet
from apps.core.utils.rest import parse_query_params
from .filters import SpentTimeFilter
from .serializers import MetricSerializer, MetricsParamsSerializer, TimeExpenseSerializer
from ..models import SpentTime
from ..utils.metrics import MetricsCalculator


class MetricsView(BaseGenericAPIView):
    def get(self, request):
        params = parse_query_params(request, MetricsParamsSerializer)

        calculator = MetricsCalculator(params['user'], params['start'], params['end'], params['group'])
        metrics = calculator.calculate()

        return Response(MetricSerializer(metrics, many=True).data)


class TimeExpensesView(mixins.ListModelMixin,
                       BaseGenericViewSet):
    queryset = SpentTime.objects.all()
    filter_backends = (DjangoFilterBackend,)
    serializer_class = TimeExpenseSerializer
    filterset_class = SpentTimeFilter
