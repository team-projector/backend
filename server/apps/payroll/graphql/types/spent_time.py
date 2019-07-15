import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType

from apps.core.graphql.connection import DataSourceConnection
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.development.graphql.types.interfaces import SpentTimeBase
from apps.payroll.models import SpentTime
from apps.payroll.services.allowed.spent_time import filter_allowed_for_user


class SpentTimeType(DjangoObjectType):
    owner = graphene.Field(SpentTimeBase)

    class Meta:
        model = SpentTime
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'SpentTime'

    def resolve_owner(self, info, **kwargs):
        return self.base

    @classmethod
    def get_queryset(cls,
                     queryset,
                     info) -> QuerySet:
        return filter_allowed_for_user(
            queryset,
            info.context.user
        )
