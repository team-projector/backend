from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins

from apps.core.rest.views import BaseGenericViewSet
from apps.core.rest.views.mixins import UpdateModelMixin
from apps.development.models import Issue
from apps.development.rest.filters import IssueProblemFilter, IssueTeamFilter
from apps.development.rest.serializers import (
    IssueCardSerializer, IssueSerializer, IssueUpdateSerializer
)
from apps.development.services.problems.issue import annotate_issues_problems


class IssuesViewset(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    UpdateModelMixin,
                    BaseGenericViewSet):
    actions_serializers = {
        'retrieve': IssueSerializer,
        'list': IssueCardSerializer,
        'update': IssueCardSerializer,
        'partial_update': IssueCardSerializer,
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
