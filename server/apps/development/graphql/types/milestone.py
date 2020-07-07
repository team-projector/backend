# -*- coding: utf-8 -*-

import graphene
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.connections import DataSourceConnection
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode
from jnt_django_graphene_toolbox.types import BaseDjangoObjectType

from apps.development.graphql.interfaces import MilestoneOwner
from apps.development.graphql.types.milestone_metrics import (
    MilestoneMetricsType,
)
from apps.development.models import Milestone
from apps.development.services.milestone.allowed import filter_allowed_for_user
from apps.development.services.milestone.metrics import get_milestone_metrics
from apps.development.services.milestone.problems import get_milestone_problems


class MilestoneType(BaseDjangoObjectType):
    """Milestone type."""

    class Meta:
        model = Milestone
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = "Milestone"

    metrics = graphene.Field(MilestoneMetricsType)
    owner = graphene.Field(MilestoneOwner)
    problems = graphene.List(graphene.String)

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get milestones."""
        return filter_allowed_for_user(queryset, info.context.user)

    def resolve_metrics(self, info, **kwargs):  # noqa: WPS110
        """Get milestone metrics."""
        return get_milestone_metrics(self)

    def resolve_problems(self, info, **kwargs):  # noqa: WPS110
        """Get milestone problems."""
        return get_milestone_problems(self)
