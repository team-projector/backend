import json
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins
from rest_framework.decorators import action

from apps.core.rest.views import BaseGenericViewSet
from apps.development.rest.filters import TeamMemberFilterBackend
from apps.development.utils.problems.issues import IssueProblemsChecker
from .serializers import IssueCardSerializer, IssueProblemSerializer, TeamCardSerializer, TeamMemberCardSerializer, \
    MilestoneCardSerializer
from ..models import Issue, Team, TeamMember, Milestone
from ..tasks import sync_project_issue

logger = logging.getLogger(__name__)


@csrf_exempt
def gl_webhook(request):
    body = json.loads(request.body.decode('utf-8'))
    if body['object_kind'] != 'issue':
        return HttpResponse()

    project_id = body['project']['id']
    issue_id = body['object_attributes']['iid']

    sync_project_issue.delay(project_id, issue_id)

    logger.info(f'gitlab webhook was triggered: project_id = {project_id}, issue_id = {issue_id}')

    return HttpResponse()


class IssuesViewset(mixins.ListModelMixin,
                    BaseGenericViewSet):
    serializer_classes = {
        'list': IssueCardSerializer
    }

    queryset = Issue.objects.all()
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend)

    search_fields = ('title',)
    filter_fields = ('state', 'due_date', 'user')
    ordering_fields = ('due_date', 'title', 'created_at')
    ordering = ('due_date',)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        if self.action == 'problems':
            checker = IssueProblemsChecker()
            queryset = checker.check(queryset)

        return queryset

    @action(detail=False,
            filter_backends=(DjangoFilterBackend,),
            filter_fields=('user',),
            serializer_class=IssueProblemSerializer)
    def problems(self, request):
        return self.list(request)


class TeamsViewset(mixins.ListModelMixin,
                   BaseGenericViewSet):
    serializer_class = TeamCardSerializer
    queryset = Team.objects.all()
    search_fields = ('title',)
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend, TeamMemberFilterBackend)
    ordering_fields = ('title',)


class TeamMembersViewset(mixins.ListModelMixin,
                         BaseGenericViewSet):
    serializer_class = TeamMemberCardSerializer
    queryset = TeamMember.objects.all()

    def filter_queryset(self, queryset):
        return queryset.filter(team_id=self.kwargs['team_pk'])


class MilestoneViewset(mixins.ListModelMixin,
                       BaseGenericViewSet):
    serializer_classes = {
        'list': MilestoneCardSerializer
    }

    queryset = Milestone.objects.all()
