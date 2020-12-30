import graphene
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.connections import DataSourceConnection
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode
from jnt_django_graphene_toolbox.types import BaseDjangoObjectType

from apps.development.graphql.interfaces import WorkItem
from apps.payroll.models import Bonus
from apps.payroll.services.salary.allowed import filter_allowed_for_user
from apps.users.graphql.types import UserType


class BonusType(BaseDjangoObjectType):
    """Bonus type."""

    class Meta:
        model = Bonus
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = "Bonus"

    owner = graphene.Field(WorkItem)
    user = graphene.Field(UserType)

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get bonuses."""
        return filter_allowed_for_user(queryset, info.context.user)
