# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.development.graphql.filters import MilestonesFilterSet
from apps.development.graphql.resolvers import resolve_milestones_summary
from apps.development.graphql.types import MilestonesSummaryType, MilestoneType


class MilestonesQueries(graphene.ObjectType):
    """Class representing list of available fields for milestone queries."""

    milestone = DatasourceRelayNode.Field(MilestoneType)

    all_milestones = DataSourceConnectionField(
        MilestoneType, filterset_class=MilestonesFilterSet,
    )

    milestones_summary = graphene.Field(
        MilestonesSummaryType, resolver=resolve_milestones_summary,
    )
