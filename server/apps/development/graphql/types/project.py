from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.models import Project
from apps.development.graphql.filters import MilestonesFilterSet
from apps.development.graphql.types.interfaces import MilestoneOwner
from apps.development.graphql.types.milestone import MilestoneType


class ProjectType(BaseDjangoObjectType):
    milestones = DataSourceConnectionField(
        MilestoneType,
        filterset_class=MilestonesFilterSet
    )

    def resolve_milestones(self, info, **kwargs):
        return self.group.milestones

    class Meta:
        model = Project
        interfaces = (DatasourceRelayNode, MilestoneOwner)
        connection_class = DataSourceConnection
        name = 'Project'
