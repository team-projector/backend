# -*- coding: utf-8 -*-

from typing import List

import django_filters
from django.db.models import QuerySet

from apps.core.graphql.filters.ordering import OrderingFilter
from apps.development.models import TeamMember
from apps.development.models.team_member import TEAM_MEMBER_ROLES
from apps.development.services.team_members import filter_by_roles


class TeamMemberRolesFilter(django_filters.CharFilter):
    """
    Filter team members by roles.
    """
    def filter(self, queryset, value) -> QuerySet:
        """
        Do filtering.
        """
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
            if val.strip() in TEAM_MEMBER_ROLES
        ]


class TeamMembersFilterSet(django_filters.FilterSet):
    """
    Set of filters for Team Member.
    """
    roles = TeamMemberRolesFilter()
    order_by = OrderingFilter(
        fields=('user__name',),
    )

    class Meta:
        model = TeamMember
        fields = ('roles',)
