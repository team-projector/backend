import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics

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


class MeIssues(generics.ListAPIView):
    serializer_class = IssueCardSerializer
    queryset = Issue.objects
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend)

    search_fields = ('title',)
    filter_fields = ('state', 'due_date')
    ordering_fields = ('due_date', 'title')
    ordering = ('due_date', 'created_at')

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(employee=self.request.user)
