from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.core.rest.mixins.views import UpdateModelMixin
from apps.core.rest.views import BaseGenericViewSet
from apps.core.utils.rest import parse_query_params, parse_data_params
from apps.development.models import Issue
from apps.development.rest.filters import IssueProblemFilter
from apps.development.rest.serializers import (
    IssueCardSerializer, IssueSerializer, IssueUpdateSerializer,
    IssuesSummarySerializer
)
from apps.development.services.gitlab.spent_time import add_spent_time
from apps.development.services.issues.problems import annotate_issues_problems
from apps.development.services.issues.summary import get_issues_summary
from apps.development.tasks import sync_project_issue
from apps.users.models import User


class GitlabAddSpentTimeSerializer(serializers.Serializer):
    time = serializers.IntegerField(min_value=1)


class IssuesSummaryParamsSerializer(serializers.Serializer):
    due_date = serializers.DateField(required=False)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )


class IssuesViewset(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    UpdateModelMixin,
                    BaseGenericViewSet):
    actions_serializers = {
        'retrieve': IssueSerializer,
        'list': IssueCardSerializer,
        'update': IssueCardSerializer,
        'partial_update': IssueCardSerializer,
        'spend': IssueSerializer,
        'sync': IssueSerializer,
        'summary': IssuesSummarySerializer
    }
    update_serializer_class = IssueUpdateSerializer
    queryset = Issue.objects.all()

    filter_backends = (
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
        IssueProblemFilter
    )
    filter_fields = ('state', 'due_date', 'user')

    search_fields = ('title',)
    ordering_fields = ('due_date', 'title', 'created_at')
    ordering = ('due_date',)

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action in ('list', 'retrieve'):
            queryset = annotate_issues_problems(queryset)

        return queryset

    @action(detail=True,
            methods=['post'])
    def spend(self, request, **kwargs):
        if not request.user.gl_token:
            raise ValidationError(_('MSG_PLEASE_PROVIDE_PERSONAL_GL_TOKEN'))

        issue = self.get_object()

        params = parse_data_params(
            request,
            GitlabAddSpentTimeSerializer
        )

        add_spent_time(
            request.user,
            issue,
            params['time']
        )

        return Response(self.get_serializer(issue).data)

    @action(detail=True,
            methods=['post'])
    def sync(self, request, pk=None):
        issue = self.get_object()
        sync_project_issue.delay(
            issue.project.gl_id,
            issue.gl_iid
        )

        return Response(self.get_serializer(self.get_object()).data)

    @action(detail=False)
    def summary(self, request):
        params = parse_query_params(
            request,
            IssuesSummaryParamsSerializer
        )

        queryset = self.get_filtered_queryset()
        return Response(self.get_serializer(
            get_issues_summary(
                queryset,
                params.get('due_date'),
                params.get('user')
            )).data)
