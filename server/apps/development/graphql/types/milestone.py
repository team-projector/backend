import graphene
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.graphql.types.interfaces import BaseWorkItem
from apps.development.models import Milestone
from apps.development.services.metrics.milestones import get_milestone_metrics
from .milestone_metrics import MilestoneMetricsType


class MilestoneType(BaseDjangoObjectType):
    owner_model = graphene.Field(BaseWorkItem)
    metrics = graphene.Field(MilestoneMetricsType)

    class Meta:
        model = Milestone
        interfaces = (DatasourceRelayNode, BaseWorkItem)
        connection_class = DataSourceConnection
        name = 'Milestone'

    def resolve_owner_model(self, info, **kwargs):
        return self.owner

    def resolve_metrics(self, info, **kwargs):
        return get_milestone_metrics(self)

    @classmethod
    def get_queryset(cls,
                     queryset,
                     info) -> QuerySet:
        if not info.context.user.roles.project_manager:
            raise PermissionDenied(
                'Only project managers can view project resources'
            )

        return queryset
