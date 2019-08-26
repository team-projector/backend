import graphene

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.models import Project
from apps.development.graphql.resolvers import resolve_milestones
from apps.development.graphql.types.interfaces import MilestoneOwner
from apps.development.graphql.types.milestone import MilestoneType


class ProjectType(BaseDjangoObjectType):
    milestones = graphene.List(
        MilestoneType,
        active=graphene.Boolean(),
        order_by=graphene.String(),
        resolver=resolve_milestones
    )

    class Meta:
        model = Project
        interfaces = (DatasourceRelayNode, MilestoneOwner)
        connection_class = DataSourceConnection
        name = 'Project'
