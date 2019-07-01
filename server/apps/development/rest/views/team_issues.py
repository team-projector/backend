from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins
from rest_framework.permissions import IsAuthenticated

from apps.core.rest.views import BaseGenericViewSet
from apps.development.models import Issue, Team
from apps.development.rest import permissions
from apps.development.rest.serializers import IssueCardSerializer


class TeamIssuesViewset(mixins.ListModelMixin,
                        BaseGenericViewSet):
    permission_classes = (
        IsAuthenticated,
        permissions.CanViewTeamData
    )
    actions_serializers = {
        'list': IssueCardSerializer
    }
    queryset = Issue.objects
    filter_backends = (
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter
    )

    search_fields = ('title',)
    filter_fields = ('state', 'due_date', 'user')
    ordering_fields = ('due_date', 'title', 'created_at')
    ordering = ('due_date',)

    @cached_property
    def team(self):
        team = get_object_or_404(
            Team.objects,
            pk=self.kwargs['team_pk']
        )
        self.check_object_permissions(self.request, team)

        return team

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(
            user__teams=self.team
        )
