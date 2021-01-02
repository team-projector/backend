import graphene
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode

from apps.core.graphql.types import BaseModelObjectType
from apps.development.graphql.fields.milestones import (
    MilestonesConnectionField,
)
from apps.development.graphql.interfaces import MilestoneOwner
from apps.development.graphql.types import TeamType
from apps.development.graphql.types.project_group_metrics import (
    ProjectGroupMetricsType,
)
from apps.development.models import ProjectGroup
from apps.development.models.choices.project_state import ProjectState
from apps.development.services.project_group.metrics import (
    get_project_group_metrics,
)


class ProjectGroupType(BaseModelObjectType):
    """Project Group type."""

    class Meta:
        model = ProjectGroup
        interfaces = (DatasourceRelayNode, MilestoneOwner)

    gl_url = graphene.String()
    gl_last_sync = graphene.DateTime()
    gl_avatar = graphene.String()
    title = graphene.String()
    full_title = graphene.String()
    is_active = graphene.Boolean()
    milestones = MilestonesConnectionField()
    team = graphene.Field(TeamType)
    state = graphene.Field(graphene.Enum.from_enum(ProjectState))

    metrics = graphene.Field(ProjectGroupMetricsType)

    def resolve_metrics(self: ProjectGroup, info, **kwargs):  # noqa: WPS110
        """Get project group metrics."""
        return get_project_group_metrics(self)
