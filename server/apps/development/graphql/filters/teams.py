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
    """Filter team by roles."""

    def filter(self, queryset, roles) -> QuerySet:  # noqa: A003
        """Do filtering."""
        parsed_roles = self._parse_roles(roles)
        if not parsed_roles:
            return queryset

        team_members = filter_by_roles(
            TeamMember.objects.filter(
                team=OuterRef('pk'),
                user=self.parent.request.user,
            ),
            parsed_roles,
        )

        queryset = queryset.annotate(
            member_exists=Exists(team_members),
        ).filter(
            member_exists=True,
        )

        return queryset

    def _parse_roles(self, roles: str) -> List[str]:
        if not roles:
            return []

        return [
            role.strip()
            for role in roles.split(',')
            if role.strip() in TEAM_MEMBER_ROLES
        ]


class TeamsFilterSet(django_filters.FilterSet):
    """Set of filters for Team."""

    roles = TeamRolesFilter()
    order_by = OrderingFilter(
        fields=('title',),
    )
    q = SearchFilter(fields=('title',))  # noqa: WPS111

    class Meta:
        model = Team
        fields = ('title', 'roles')
