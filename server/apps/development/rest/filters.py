from distutils.util import strtobool

from django.db.models import Exists, OuterRef
from rest_framework import filters

from apps.core.rest.filters import FilterParamUrlSerializer
from apps.core.utils.rest import parse_query_params
from apps.development.models import Milestone, TeamMember
from apps.development.rest.serializers import TeamMemberFilterSerializer, TeamMemberRoleFilterSerializer
from apps.development.services.team_members import filter_by_roles


class TeamMemberFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = parse_query_params(request, TeamMemberFilterSerializer)

        user, roles = params.get('user'), params.get('roles')

        if all(param is not None for param in (user, roles)):
            team_members = filter_by_roles(
                TeamMember.objects.filter(
                    team=OuterRef('pk'),
                    user=user,
                ), roles)

            queryset = queryset.annotate(
                member_exists=Exists(team_members)
            ).filter(
                member_exists=True
            )

        return queryset


class TeamMemberRoleFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = parse_query_params(request, TeamMemberRoleFilterSerializer)

        roles = params.get('roles')
        if roles:
            queryset = filter_by_roles(queryset, roles)

        return queryset


class MilestoneActiveFiler(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        active_param = request.GET.get('active')

        if not active_param:
            return queryset

        if strtobool(active_param):
            return queryset.filter(state=Milestone.STATE.active)

        return queryset.filter(state=Milestone.STATE.closed)


class IssueStatusUrlFiler(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = parse_query_params(request, FilterParamUrlSerializer)

        gl_url = params.get('url')

        if gl_url:
            queryset = queryset.filter(gl_url=gl_url)

        return queryset
