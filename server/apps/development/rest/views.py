import json
import logging

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.core.activity.verbs import ACTION_GITLAB_WEBHOOK_TRIGGERED
from apps.core.rest.mixins.views import CreateModelMixin, UpdateModelMixin
from apps.core.rest.views import BaseGenericAPIView, BaseGenericViewSet
from apps.core.tasks import add_action
from apps.development.rest import permissions
from apps.development.rest.filters import IssueStatusUrlFiler, MilestoneActiveFiler, TeamMemberFilterBackend
from apps.development.services.problems.issues import IssueProblemsChecker
from apps.development.services.status.gitlab import get_gitlab_sync_status
from .serializers import (FeatureCardSerializer, FeatureSerializer, FeatureUpdateSerializer,
                          GitlabIssieStatusSerializer, GitlabStatusSerializer, IssueCardSerializer,
                          IssueProblemSerializer, IssueSerializer, IssueUpdateSerializer, MilestoneCardSerializer,
                          TeamCardSerializer, TeamMemberCardSerializer, TeamSerializer)
from ..models import Feature, Issue, Milestone, Team, TeamMember
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
    add_action.delay(verb=ACTION_GITLAB_WEBHOOK_TRIGGERED)

    return HttpResponse()


class IssuesViewset(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    UpdateModelMixin,
                    BaseGenericViewSet):
    serializer_classes = {
        'retrieve': IssueSerializer,
        'list': IssueCardSerializer,
        'update': IssueCardSerializer,
        'partial_update': IssueCardSerializer,
    }
    update_serializer_class = IssueUpdateSerializer

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
                   mixins.RetrieveModelMixin,
                   BaseGenericViewSet):
    serializer_classes = {
        'list': TeamCardSerializer,
        'retrieve': TeamSerializer,
    }
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


class MilestoneIssuesViewset(mixins.ListModelMixin,
                             BaseGenericViewSet):
    permission_classes = (IsAuthenticated, permissions.IsProjectManager)

    serializer_classes = {
        'list': IssueCardSerializer
    }

    queryset = Issue.objects.all()

    @cached_property
    def milestone(self):
        return get_object_or_404(Milestone.objects, pk=self.kwargs['milestone_pk'])

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset.filter(milestone=self.milestone))


class MilestoneFeaturesViewset(mixins.ListModelMixin,
                               BaseGenericViewSet):
    permission_classes = (IsAuthenticated, permissions.IsProjectManager)

    serializer_classes = {
        'list': FeatureCardSerializer
    }

    queryset = Feature.objects.all()

    @cached_property
    def milestone(self):
        return get_object_or_404(Milestone.objects, pk=self.kwargs['milestone_pk'])

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset.filter(milestone=self.milestone))


class FeaturesViewset(CreateModelMixin,
                      UpdateModelMixin,
                      BaseGenericViewSet):
    permission_classes = (IsAuthenticated, permissions.IsProjectManager)

    serializer_classes = {
        'create': FeatureSerializer,
        'update': FeatureSerializer,
        'partial_update': FeatureSerializer,
    }
    update_serializer_class = FeatureUpdateSerializer

    queryset = Feature.objects.all()


class FeatureIssuesViewset(mixins.ListModelMixin, BaseGenericViewSet):
    permission_classes = (IsAuthenticated, permissions.IsProjectManager)

    serializer_classes = {
        'list': IssueCardSerializer
    }

    queryset = Issue.objects.all()

    @cached_property
    def feature(self):
        return get_object_or_404(Feature.objects, pk=self.kwargs['feature_pk'])

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset.filter(feature=self.feature))


class GitlabStatusView(BaseGenericAPIView):
    serializer_class = GitlabStatusSerializer

    def get(self, request):
        status = get_gitlab_sync_status()

        return Response(self.get_serializer(status).data)


class MilestonesViewset(mixins.ListModelMixin,
                        BaseGenericViewSet):
    permission_classes = (IsAuthenticated, permissions.IsProjectManager,)

    serializer_classes = {
        'list': MilestoneCardSerializer
    }

    queryset = Milestone.objects.all()
    filter_backends = (filters.OrderingFilter, MilestoneActiveFiler,)
    ordering = ('-due_date',)


class MilestoneIssuesOrphanViewset(mixins.ListModelMixin,
                                   BaseGenericViewSet):
    permission_classes = (IsAuthenticated, permissions.IsProjectManager)

    serializer_classes = {
        'list': IssueCardSerializer
    }

    queryset = Issue.objects.all()

    @cached_property
    def milestone(self):
        return get_object_or_404(Milestone.objects, pk=self.kwargs['milestone_pk'])

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset.filter(milestone=self.milestone, feature__isnull=True))


class GitlabIssueStatusView(BaseGenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = GitlabIssieStatusSerializer
    queryset = Issue.objects.all()
    filter_backends = (IssueStatusUrlFiler,)

    def get(self, request, format=None):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(self.get_serializer(queryset.first()).data)


class TeamIssueProblemsViewset(mixins.ListModelMixin,
                               BaseGenericViewSet):
    permission_classes = (IsAuthenticated, permissions.IsTeamLeader)
    serializer_classes = {
        'list': IssueProblemSerializer
    }
    queryset = Issue.objects
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('user',)

    @cached_property
    def team(self):
        team = get_object_or_404(Team.objects, pk=self.kwargs['team_pk'])
        self.check_object_permissions(self.request, team)

        return team

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset).filter(user__team_members__team=self.team)

        checker = IssueProblemsChecker()
        queryset = checker.check(queryset)

        return queryset


class TeamIssuesViewset(mixins.ListModelMixin,
                        BaseGenericViewSet):
    permission_classes = (IsAuthenticated, permissions.IsTeamLeader,)
    serializer_classes = {
        'list': IssueCardSerializer
    }
    queryset = Issue.objects
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    search_fields = ('title',)
    filter_fields = ('state', 'due_date', 'user')
    ordering_fields = ('due_date', 'title', 'created_at')

    @cached_property
    def team(self):
        team = get_object_or_404(Team.objects, pk=self.kwargs['team_pk'])
        self.check_object_permissions(self.request, team)

        return team

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(user__team_members__team=self.team)
