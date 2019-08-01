import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.development.graphql.filters import MilestonesFilterSet
from apps.development.graphql.types import MilestoneType


class MilestonesQueries(graphene.ObjectType):
    all_milestones = DataSourceConnectionField(
        MilestoneType,
        filterset_class=MilestonesFilterSet
    )