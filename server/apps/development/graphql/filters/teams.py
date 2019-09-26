# -*- coding: utf-8 -*-

from typing import List

import django_filters
from django.db.models import Exists, OuterRef, QuerySet

from apps.core.graphql.filters import SearchFilter
from apps.core.graphql.filters.ordering import OrderingFilter
from apps.development.models import Team, TeamMember
from apps.development.models.team_member import TEAM_MEMBER_ROLES
from apps.development.services.team_members import filter_by_roles


class TeamRolesFilter(django_filters.CharFilter):
    def filter(self, queryset, value) -> QuerySet:
        roles = self._parse_roles(value)
        if not roles:
            return queryset

        team_members = filter_by_roles(
            TeamMember.objects.filter(
                team=OuterRef('pk'),
                user=self.parent.request.user,
            ), roles)

        queryset = queryset.annotate(
            member_exists=Exists(team_members),
        ).filter(
            member_exists=True,
        )

        return queryset

    def _parse_roles(self, value: str) -> List[str]:
        if not value:
            return []

        return [
            val.strip()
            for val in value.split(',')
            if val.strip() in TEAM_MEMBER_ROLES
        ]


class TeamsFilterSet(django_filters.FilterSet):
    roles = TeamRolesFilter()
    order_by = OrderingFilter(
        fields=('title',),
    )
    q = SearchFilter(fields=('title',))

    class Meta:
        model = Team
        fields = ('title', 'roles')
