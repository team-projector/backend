from rest_framework.response import Response

from apps.core.rest.views import BaseGenericAPIView
from .serializers import MetricSerializer, MetricsParamsSerializer
from ..utils.metrics import MetricsCalculator


class MetricsView(BaseGenericAPIView):
    def get(self, request):
        params = self.get_params(request)

        calculator = MetricsCalculator(params['user'], params['start'], params['end'], params['group'])
        metrics = calculator.calculate()

        return Response(MetricSerializer(metrics, many=True).data)

    def get_params(self, request):
        serializer = MetricsParamsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        return serializer.validated_data
