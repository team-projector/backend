import graphene
from graphene_django import DjangoObjectType

from apps.core.graphql.connection import DataSourceConnection
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.development.graphql.types.interfaces import WorkItem
from apps.development.models import Milestone
from apps.development.services.metrics.milestones import get_milestone_metrics
from .milestone_metrics import MilestoneMetricsType


class MilestoneType(DjangoObjectType):
    metrics = graphene.Field(MilestoneMetricsType)

    class Meta:
        model = Milestone
        interfaces = (DatasourceRelayNode, WorkItem)
        connection_class = DataSourceConnection
        name = 'Milestone'

    def resolve_metrics(self, info, **kwargs):
        return get_milestone_metrics(self)
