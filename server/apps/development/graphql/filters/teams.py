# -*- coding: utf-8 -*-

from typing import List

import django_filters
from django.db.models import Exists, OuterRef, QuerySet
from jnt_django_graphene_toolbox.filters import OrderingFilter, SearchFilter

from apps.development.models import Team, TeamMember
from apps.development.models.team_member import TeamMemberRole
from apps.development.services.team_members import filter_by_roles


class TeamRolesFilter(django_filters.CharFilter):
    """Filter team by roles."""

    def filter(self, queryset, roles) -> QuerySet:  # noqa: WPS125, A003
        """Do filtering."""
        parsed_roles = self._parse_roles(roles)
        if not parsed_roles:
            return queryset

        team_members = filter_by_roles(
            TeamMember.objects.filter(
                team=OuterRef("pk"), user=self.parent.request.user,
            ),
            parsed_roles,
        )

        return queryset.annotate(member_exists=Exists(team_members)).filter(
            member_exists=True,
        )

    def _parse_roles(self, roles: str) -> List[str]:
        if not roles:
            return []

        return [
            role.strip()
            for role in roles.split(",")
            if role.strip() in TeamMemberRole
        ]


class TeamsFilterSet(django_filters.FilterSet):
    """Set of filters for Team."""

    class Meta:
        model = Team
        fields = ("title", "roles")

    roles = TeamRolesFilter()
    order_by = OrderingFilter(fields=("title",))
    q = SearchFilter(fields=("title",))  # noqa: WPS111
