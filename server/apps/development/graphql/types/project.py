import graphene
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode

from apps.core.graphql.types import BaseModelObjectType
from apps.development.graphql.fields.milestones import (
    MilestonesConnectionField,
)
from apps.development.graphql.interfaces import MilestoneOwner
from apps.development.graphql.resolvers.project_milestones import (
    resolve_project_milestones,
)
from apps.development.graphql.types import ProjectMetricsType
from apps.development.models import Project
from apps.development.models.choices.project_state import ProjectState
from apps.development.services.project.metrics import get_project_metrics


class ProjectType(BaseModelObjectType):
    """Project type."""

    class Meta:
        model = Project
        interfaces = (DatasourceRelayNode, MilestoneOwner)
        auth_required = True

    gl_url = graphene.String()
    gl_last_sync = graphene.DateTime()
    gl_avatar = graphene.String()
    title = graphene.String()
    full_title = graphene.String()
    is_active = graphene.Boolean()
    state = graphene.Field(graphene.Enum.from_enum(ProjectState))
    group = graphene.Field("apps.development.graphql.types.ProjectGroupType")
    milestones = MilestonesConnectionField()
    metrics = graphene.Field(ProjectMetricsType)
    team = graphene.Field("apps.development.graphql.types.TeamType")

    def resolve_milestones(self: Project, info, **kwargs):  # noqa: WPS110
        """Get project milestones."""
        return resolve_project_milestones(self, info, **kwargs)

    def resolve_metrics(self: Project, info, **kwargs):  # noqa: WPS110
        """Get project metrics."""
        return get_project_metrics(self)
