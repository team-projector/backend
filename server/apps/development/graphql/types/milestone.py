import graphene
from django.db.models import QuerySet

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.graphql.types.interfaces import Owner
from apps.development.models import Milestone
from apps.development.services.allowed.milestones import filter_allowed_for_user
from apps.development.services.metrics.milestones import get_milestone_metrics
from .milestone_metrics import MilestoneMetricsType


class MilestoneType(BaseDjangoObjectType):
    owner = graphene.Field(Owner)
    metrics = graphene.Field(MilestoneMetricsType)

    class Meta:
        model = Milestone
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'Milestone'

    def resolve_metrics(self, info, **kwargs):
        return get_milestone_metrics(self)

    @classmethod
    def get_queryset(cls,
                     queryset,
                     info) -> QuerySet:
        queryset = filter_allowed_for_user(
            queryset,
            info.context.user
        )

        return queryset
