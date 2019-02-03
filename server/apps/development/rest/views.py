import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins

from apps.core.rest.views import BaseGenericViewSet
from .serializers import IssueCardSerializer
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
