from distutils.util import strtobool


from django.db.models import Exists, OuterRef, Q
from rest_framework import filters

from apps.core.rest.filters import FilterParamUrlSerializer
from apps.core.utils.rest import parse_query_params
from apps.development.models import TeamMember, Milestone
from apps.development.rest.serializers import TeamMemberFilterSerializer


class TeamMemberFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = parse_query_params(request, TeamMemberFilterSerializer)

        user, roles = params.get('user'), params.get('roles')

        if user is not None and roles is not None:
            team_members = TeamMember.objects.filter(team=OuterRef('pk'), user=user, roles=roles)
            queryset = queryset.annotate(member_exists=Exists(team_members)).filter(member_exists=True)

        return queryset


class TeamMemberRoleFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        param_roles = request.GET.get('roles')

        if param_roles:
            roles = self.parse_list(param_roles)

            return queryset.filter(self.get_query_filter_roles(roles))

        return queryset

    @staticmethod
    def parse_list(l):
        return l.split(',')

    @staticmethod
    def get_query_filter_roles(roles):
        map_roles = {
            'leader': TeamMember.roles.leader,
            'developer': TeamMember.roles.developer,
            'watcher': TeamMember.roles.watcher,
        }

        filter_roles = Q()
        for role in roles:
            filter_roles |= Q(roles=map_roles.get(role))

        return filter_roles


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
