from typing import List

import django_filters
import graphene
from django.db.models import Exists, OuterRef, QuerySet
from jnt_django_graphene_toolbox.filters import SearchFilter

from apps.core.graphql.fields import BaseModelConnectionField
from apps.core.graphql.queries.filters import OrderingFilter
from apps.development.models import Team, TeamMember
from apps.development.models.team_member import TeamMemberRole
from apps.development.services.team_members.filters import filter_by_roles


class TeamRolesFilter(django_filters.CharFilter):
    """Filter team by roles."""

    def filter(self, queryset, roles) -> QuerySet:  # noqa: WPS125, A003
        """Do filtering."""
        parsed_roles = self._parse_roles(roles)
        if not parsed_roles:
            return queryset

        team_members = filter_by_roles(
            TeamMember.objects.filter(
                team=OuterRef("pk"),
                user=self.parent.request.user,
            ),
            parsed_roles,
        )

        return queryset.annotate(member_exists=Exists(team_members)).filter(
            member_exists=True,
        )

    def _parse_roles(self, roles: str) -> List[str]:
        """
        Parse roles.

        :param roles:
        :type roles: str
        :rtype: List[str]
        """
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


class AllTeamsConnectionField(BaseModelConnectionField):
    """Handler for users collections."""

    filterset_class = TeamsFilterSet

    def __init__(self):
        """Initialize."""
        super().__init__(
            "development.TeamType",
            title=graphene.String(),
            roles=graphene.String(),
            q=graphene.String(),
            order_by=graphene.String(),  # "title"
        )
