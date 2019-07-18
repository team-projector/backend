import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType

from apps.core.graphql.connection import DataSourceConnection
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.development.graphql.types.interfaces import SpentTimeBase
from apps.payroll.models import Salary
from apps.payroll.services.allowed.salary import filter_allowed_for_user


class SalaryType(DjangoObjectType):
    owner = graphene.Field(SpentTimeBase)

    class Meta:
        model = Salary
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'Salary'

    @classmethod
    def get_queryset(cls,
                     queryset,
                     info) -> QuerySet:
        return filter_allowed_for_user(
            queryset,
            info.context.user
        )
