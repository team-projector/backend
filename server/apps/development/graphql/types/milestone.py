# -*- coding: utf-8 -*-

import graphene
from django.db.models import QuerySet

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.graphql.types.interfaces import MilestoneOwner
from apps.development.models import Milestone
from apps.development.services import milestone as milestone_service

from .milestone_metrics import MilestoneMetricsType


class MilestoneType(BaseDjangoObjectType):
    """Milestone type."""

    metrics = graphene.Field(MilestoneMetricsType)
    owner = graphene.Field(MilestoneOwner)
    problems = graphene.List(graphene.String)

    class Meta:
        model = Milestone
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'Milestone'

    def resolve_metrics(self, info, **kwargs):  # noqa WPS110
        """Get milestone metrics."""
        return milestone_service.get_metrics(self)

    def resolve_problems(self, info, **kwargs):  # noqa WPS110
        """Get milestone problems."""
        return milestone_service.get_problems(self)

    @classmethod
    def get_queryset(
        cls,
        queryset,
        info,  # noqa WPS110
    ) -> QuerySet:
        """Get milestones."""
        queryset = milestone_service.filter_allowed_for_user(
            queryset,
            info.context.user,
        )

        return queryset
