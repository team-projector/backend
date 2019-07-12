import graphene
from graphene_django import DjangoObjectType

from apps.core.graphql.connection import DataSourceConnection
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.payroll.services.metrics.user import UserMetricsProvider
from apps.users.models import User
from .user_metrics import UserMetricsType


class UserType(DjangoObjectType):
    metrics = graphene.Field(UserMetricsType)

    class Meta:
        model = User
        exclude_fields = ('password',)
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'User'

    def resolve_metrics(self, info, **kwargs):
        provider = UserMetricsProvider()
        return provider.get_metrics(self)
