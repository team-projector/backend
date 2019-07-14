from typing import List

import django_filters
from django.db.models import QuerySet

from apps.development.models import TeamMember
from apps.development.services.team_members import filter_by_roles


class TeamMemberRolesFilter(django_filters.CharFilter):
    def filter(self, queryset, value) -> QuerySet:
        roles = self._parse_roles(value)
        if not roles:
            return queryset

        return filter_by_roles(queryset, roles)

    def _parse_roles(self, value: str) -> List[str]:
        if not value:
            return []

        return [
            val.strip()
            for val in value.split(',')
            if val.strip() in TeamMember.ROLES
        ]


class TeamMembersFilterSet(django_filters.FilterSet):
    roles = TeamMemberRolesFilter()
    order_by = django_filters.OrderingFilter(
        fields=('user__name',)
    )

    class Meta:
        model = TeamMember
        fields = ('roles',)