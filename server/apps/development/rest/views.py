import json
import logging

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.activity.verbs import ACTION_GITLAB_WEBHOOK_TRIGGERED
from apps.core.rest.mixins.views import CreateModelMixin, UpdateModelMixin
from apps.core.rest.views import BaseGenericViewSet, BaseGenericAPIView
from apps.core.tasks import add_action
from apps.development.rest import permissions
from apps.development.rest.filters import TeamMemberFilterBackend
from apps.development.utils.problems.issues import IssueProblemsChecker
from .serializers import IssueCardSerializer, IssueProblemSerializer, TeamCardSerializer, TeamMemberCardSerializer, \
    MilestoneCardSerializer, EpicCardSerializer, EpicUpdateSerializer, EpicSerializer, GitlabStatusSerializer
from ..models import Issue, Team, TeamMember, Milestone, ProjectGroup, Project, Epic
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
    add_action.delay(request.user, verb=ACTION_GITLAB_WEBHOOK_TRIGGERED)

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


class ProjectGroupMilestonesViewset(mixins.ListModelMixin,
                                    mixins.RetrieveModelMixin,
                                    BaseGenericViewSet):
    permission_classes = (permissions.IsProjectManager,)

    serializer_classes = {
        'retrieve': MilestoneCardSerializer,
        'list': MilestoneCardSerializer
    }

    queryset = Milestone.objects.all()

    @cached_property
    def project_group(self):
        return get_object_or_404(ProjectGroup.objects, pk=self.kwargs['project_group_pk'])

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset.filter(project_group=self.project_group))


class ProjectMilestonesViewset(mixins.ListModelMixin,
                               BaseGenericViewSet):
    permission_classes = (permissions.IsProjectManager,)

    serializer_classes = {
        'list': MilestoneCardSerializer
    }

    queryset = Milestone.objects.all()

    @cached_property
    def project(self):
        return get_object_or_404(Project.objects, pk=self.kwargs['project_pk'])

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset.filter(project=self.project))


class MilestoneIssuesViewset(mixins.ListModelMixin, BaseGenericViewSet):
    permission_classes = (permissions.IsProjectManager,)

    serializer_classes = {
        'list': IssueCardSerializer
    }

    queryset = Issue.objects.all()

    @cached_property
    def milestone(self):
        return get_object_or_404(Milestone.objects, pk=self.kwargs['milestone_pk'])

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset.filter(milestone=self.milestone))


class MilestoneEpicsViewset(mixins.ListModelMixin, BaseGenericViewSet):
    permission_classes = (permissions.IsProjectManager,)

    serializer_classes = {
        'list': EpicCardSerializer
    }

    queryset = Epic.objects.all()

    @cached_property
    def milestone(self):
        return get_object_or_404(Milestone.objects, pk=self.kwargs['milestone_pk'])

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset.filter(milestone=self.milestone))


class EpicsViewset(CreateModelMixin,
                   UpdateModelMixin,
                   BaseGenericViewSet):
    permission_classes = (permissions.IsProjectManager,)

    serializer_classes = {
        'create': EpicSerializer,
        'update': EpicSerializer,
        'partial_update': EpicSerializer,
    }
    update_serializer_class = EpicUpdateSerializer

    queryset = Epic.objects.all()

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset)


class EpicIssuesViewset(mixins.ListModelMixin, BaseGenericViewSet):
    permission_classes = (permissions.IsProjectManager,)

    serializer_classes = {
        'list': IssueCardSerializer
    }

    queryset = Issue.objects.all()

    @cached_property
    def epic(self):
        return get_object_or_404(Epic.objects, pk=self.kwargs['epic_pk'])

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset.filter(milestone__epic=self.epic))


class GitlabStatusView(BaseGenericAPIView):
    serializer_class = GitlabStatusSerializer

    def get(self, request):
        return Response(self.get_serializer(request).data)
