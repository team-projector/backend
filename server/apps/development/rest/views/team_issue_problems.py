from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated

from apps.core.rest.views import BaseGenericViewSet
from apps.development.models import Issue, Team
from apps.development.rest import permissions
from apps.development.rest.serializers import IssueProblemSerializer
from apps.development.services.problems.issues import IssueProblemsChecker


class TeamIssueProblemsViewset(mixins.ListModelMixin,
                               BaseGenericViewSet):
    permission_classes = (
        IsAuthenticated,
        permissions.IsTeamLeader
    )
    serializer_classes = {
        'list': IssueProblemSerializer
    }
    queryset = Issue.objects
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('user',)

    @cached_property
    def team(self):
        team = get_object_or_404(
            Team.objects,
            pk=self.kwargs['team_pk']
        )
        self.check_object_permissions(self.request, team)

        return team

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset).filter(
            user__team_members__team=self.team
        )

        checker = IssueProblemsChecker()
        queryset = checker.check(queryset)

        return queryset
