import graphene
from jnt_django_graphene_toolbox.connection_fields import (
    DataSourceConnectionField,
)
from jnt_django_graphene_toolbox.connections import DataSourceConnection
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode
from jnt_django_graphene_toolbox.types import BaseDjangoObjectType

from apps.development.graphql.filters import MilestonesFilterSet
from apps.development.graphql.interfaces import MilestoneOwner
from apps.development.graphql.resolvers.project_milestones import (
    resolve_project_milestones,
)
from apps.development.graphql.types import ProjectMetricsType, TeamType
from apps.development.graphql.types.milestone import MilestoneType
from apps.development.models import Project
from apps.development.services.project.metrics import get_project_metrics


class ProjectType(BaseDjangoObjectType):
    """Project type."""

    class Meta:
        model = Project
        interfaces = (DatasourceRelayNode, MilestoneOwner)
        connection_class = DataSourceConnection
        name = "Project"

    milestones = DataSourceConnectionField(
        MilestoneType,
        filterset_class=MilestonesFilterSet,
    )
    metrics = graphene.Field(ProjectMetricsType)
    team = graphene.Field(TeamType)

    def resolve_milestones(self: Project, info, **kwargs):  # noqa: WPS110
        """Get project milestones."""
        return resolve_project_milestones(self, info, **kwargs)

    def resolve_metrics(self: Project, info, **kwargs):  # noqa: WPS110
        """Get project metrics."""
        return get_project_metrics(self)
