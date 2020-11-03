import graphene
from graphene_django import DjangoObjectType
from jnt_django_graphene_toolbox.connections import DataSourceConnection
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode

from apps.development.graphql.interfaces import MilestoneOwner
from apps.development.graphql.types.project_group_metrics import (
    ProjectGroupMetricsType,
)
from apps.development.models import ProjectGroup
from apps.development.services.project_group.metrics import (
    get_project_group_metrics,
)


class ProjectGroupType(DjangoObjectType):
    """Project Group type."""

    class Meta:
        model = ProjectGroup
        interfaces = (DatasourceRelayNode, MilestoneOwner)
        connection_class = DataSourceConnection
        name = "ProjectGroup"

    metrics = graphene.Field(ProjectGroupMetricsType)

    def resolve_metrics(self: ProjectGroup, info, **kwargs):  # noqa: WPS110
        """Get project group metrics."""
        return get_project_group_metrics(self)
