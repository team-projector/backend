from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins

from apps.core.rest.views import BaseGenericViewSet
from apps.development.models import Team, TeamMember
from apps.development.rest.filters import TeamMemberRoleFilterBackend
from apps.development.rest.serializers import TeamMemberCardSerializer


class TeamMembersViewset(mixins.ListModelMixin,
                         BaseGenericViewSet):
    serializer_class = TeamMemberCardSerializer
    queryset = TeamMember.objects.all()
    filter_backends = (
        DjangoFilterBackend,
        TeamMemberRoleFilterBackend
    )

    @cached_property
    def team(self):
        return get_object_or_404(
            Team.objects,
            pk=self.kwargs['team_pk']
        )

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(
            team=self.team
        )
