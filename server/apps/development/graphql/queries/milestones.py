import graphene

from apps.core.graphql.nodes import ModelRelayNode
from apps.development.graphql.fields import AllMilestonesConnectionField
from apps.development.graphql.resolvers import resolve_milestones_summary
from apps.development.graphql.types import MilestonesSummaryType, MilestoneType


class MilestonesQueries(graphene.ObjectType):
    """Class represents list of available fields for milestone queries."""

    milestone = ModelRelayNode.Field(MilestoneType)
    all_milestones = AllMilestonesConnectionField()
    milestones_summary = graphene.Field(
        MilestonesSummaryType,
        resolver=resolve_milestones_summary,
    )
