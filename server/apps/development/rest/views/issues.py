from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.core.rest.views import BaseGenericViewSet
from apps.core.rest.views.mixins import UpdateModelMixin
from apps.core.utils.rest import parse_data_params
from apps.development.models import Issue
from apps.development.rest.filters import IssueProblemFilter, IssueTeamFilter
from apps.development.rest.serializers import (
    IssueCardSerializer, IssueSerializer, IssueUpdateSerializer
)
from apps.development.services.gitlab.spent_time import add_spent_time
from apps.development.services.problems.issue import annotate_issues_problems


class GitlabAddSpentTimeSerializer(serializers.Serializer):
    time = serializers.IntegerField(min_value=1)


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
    }
    update_serializer_class = IssueUpdateSerializer

    filter_backends = (
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
        IssueProblemFilter,
        IssueTeamFilter
    )
    filter_fields = ('state', 'due_date', 'user')

    search_fields = ('title',)
    ordering_fields = ('due_date', 'title', 'created_at')
    ordering = ('due_date',)

    def get_queryset(self):
        queryset = Issue.objects.allowed_for_user(self.request.user)

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
