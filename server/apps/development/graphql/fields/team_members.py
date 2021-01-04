from typing import List

import django_filters
import graphene
from django.db.models import QuerySet

from apps.core.graphql.fields import BaseModelConnectionField
from apps.core.graphql.queries.filters import OrderingFilter
from apps.development.models import TeamMember
from apps.development.models.team_member import TeamMemberRole
from apps.development.services.team_members.filters import filter_by_roles


class TeamMemberRolesFilter(django_filters.CharFilter):
    """Filter team members by roles."""

    def filter(self, queryset, roles) -> QuerySet:  # noqa: WPS125, A003
        """Do filtering."""
        parsed_roles = self._parse_roles(roles)
        if not parsed_roles:
            return queryset

        return filter_by_roles(queryset, parsed_roles)

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


class TeamMembersFilterSet(django_filters.FilterSet):
    """Set of filters for Team Member."""

    class Meta:
        model = TeamMember
        fields = ("roles",)

    roles = TeamMemberRolesFilter()
    order_by = OrderingFilter(fields=("user__name",))


class TeamMembersConnectionField(BaseModelConnectionField):
    """Handler for team members collections."""

    filterset_class = TeamMembersFilterSet
    auth_required = True

    def __init__(self):
        """Initialize."""
        super().__init__(
            "apps.development.graphql.types.TeamMemberType",
            roles=graphene.String(),
            order_by=graphene.String(),  # "user__name"
        )
