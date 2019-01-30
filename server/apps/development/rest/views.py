import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins
from rest_framework.response import Response

from apps.core.rest.views import BaseGenericAPIView, BaseGenericViewSet
from apps.development.utils.metrics import MetricsCalculator
from .serializers import IssueCardSerializer, MetricSerializer, MetricsParamsSerializer
from ..models import Issue
from ..tasks import sync_project_issue


@csrf_exempt
def gl_webhook(request):
    body = json.loads(request.body.decode('utf-8'))
    if body['object_kind'] != 'issue':
        return HttpResponse()

    sync_project_issue.delay(body['project']['id'], body['object_attributes']['iid'])

    return HttpResponse()


class IssuesViewset(mixins.ListModelMixin,
                    BaseGenericViewSet):
    serializer_classes = {
        'list': IssueCardSerializer
    }

    queryset = Issue.objects.all()
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend)

    search_fields = ('title',)
    filter_fields = ('state', 'due_date', 'employee')
    ordering_fields = ('due_date', 'title', 'created_at')
    ordering = ('due_date',)


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
