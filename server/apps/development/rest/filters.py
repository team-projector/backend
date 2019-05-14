from django.db.models import OuterRef, Exists
from django.utils import timezone
from rest_framework import filters

from apps.core.utils.rest import parse_query_params
from apps.development.models import TeamMember
from apps.development.rest.serializers import TeamMemberFilterSerializer


class TeamMemberFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = parse_query_params(request, TeamMemberFilterSerializer)

        user, roles = params.get('user'), params.get('roles')

        if user is not None and roles is not None:
            team_members = TeamMember.objects.filter(team=OuterRef('pk'), user=user, roles=roles)
            queryset = queryset.annotate(member_exists=Exists(team_members)).filter(member_exists=True)

        return queryset


class MilestoneCommonFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        active_param = request.GET.get('active')

        if active_param and active_param == 'true':
            queryset = queryset.filter(start_date__lte=timezone.now().date(),
                                       due_date__gte=timezone.now().date())

        return queryset
