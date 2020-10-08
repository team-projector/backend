import graphene
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.connections import DataSourceConnection
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode
from jnt_django_graphene_toolbox.types import BaseDjangoObjectType

from apps.development.graphql.interfaces import WorkItem
from apps.payroll.models import SpentTime
from apps.payroll.services.spent_time.allowed import filter_allowed_for_user


class SpentTimeType(BaseDjangoObjectType):
    """Spent Time type."""

    class Meta:
        model = SpentTime
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = "SpentTime"

    owner = graphene.Field(WorkItem)

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get spent times."""
        return filter_allowed_for_user(queryset, info.context.user)

    def resolve_owner(self, info, **kwargs):  # noqa: WPS110
        """Get spent time owner: issue or merge request."""
        return self.base
