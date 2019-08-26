import graphene
from django.db.models import QuerySet

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.graphql.types.interfaces import MilestoneOwner
from apps.development.models import Milestone
from apps.development.services.allowed.milestones import filter_allowed_for_user
from apps.development.services.metrics.milestones import get_milestone_metrics
from apps.development.services.problems.milestone import get_milestone_problems
from .milestone_metrics import MilestoneMetricsType


class MilestoneType(BaseDjangoObjectType):
    metrics = graphene.Field(MilestoneMetricsType)
    owner = graphene.Field(MilestoneOwner)
    problems = graphene.List(graphene.String)

    class Meta:
        model = Milestone
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'Milestone'

    def resolve_metrics(self, info, **kwargs):
        return get_milestone_metrics(self)

    def resolve_problems(self, info, **kwargs):
        return get_milestone_problems(self)

    @classmethod
    def get_queryset(cls,
                     queryset,
                     info) -> QuerySet:
        queryset = filter_allowed_for_user(
            queryset,
            info.context.user
        )

        return queryset
