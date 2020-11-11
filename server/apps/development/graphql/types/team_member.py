from django.db.models import QuerySet
from jnt_django_graphene_toolbox.connections import DataSourceConnection
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode

from apps.development.models import TeamMember
from apps.users.graphql.types import UserType


class TeamMemberType(UserType):
    """Team member type."""

    class Meta:
        model = TeamMember
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = "TeamMember"

    @classmethod
    def get_queryset(
        cls,
        queryset: QuerySet,
        info,  # noqa: WPS110
    ) -> QuerySet:
        """Get queryset."""
        return queryset.filter(user__is_active=True)
