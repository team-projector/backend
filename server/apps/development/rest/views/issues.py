from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.rest.mixins.views import UpdateModelMixin
from apps.core.rest.views import BaseGenericViewSet
from apps.development.models import Issue
from apps.development.rest.serializers import (
    IssueCardSerializer, IssueProblemSerializer, IssueSerializer, IssueUpdateSerializer
)
from apps.development.services.gitlab.spent_time import add_spent_time
from apps.development.services.problems.issues import IssueProblemsChecker
from apps.development.tasks import sync_project_issue


class GitlabAddSpentTimeSerializer(serializers.Serializer):
    time = serializers.IntegerField(min_value=1)


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
    filter_backends = (
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend
    )

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

    @action(detail=True,
            methods=['post'],
            serializer_class=IssueSerializer)
    def spend(self, request, **kwargs):
        if not request.user.gl_token:
            raise ValidationError(_('MSG_PLEASE_PROVIDE_PERSONAL_GL_TOKEN'))

        issue = self.get_object()

        time_serializer = GitlabAddSpentTimeSerializer(data=request.data)
        time_serializer.is_valid(raise_exception=True)

        add_spent_time(
            request.user,
            issue,
            time_serializer.validated_data['time']
        )

        return Response(self.get_serializer(issue).data)

    @action(detail=True,
            methods=['post'],
            serializer_class=IssueSerializer,
            permission_classes=(IsAuthenticated,))
    def sync(self, request, pk=None):
        issue = self.get_object()
        sync_project_issue.delay(issue.project.gl_id, issue.gl_iid)

        return Response(self.get_serializer(self.get_object()).data)
