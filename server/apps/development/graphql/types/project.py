# -*- coding: utf-8 -*-

from datetime import datetime

from jnt_django_graphene_toolbox.connection_fields import (
    DataSourceConnectionField,
)
from jnt_django_graphene_toolbox.connections import DataSourceConnection
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode
from jnt_django_graphene_toolbox.types import BaseDjangoObjectType

from apps.development.graphql.filters import MilestonesFilterSet
from apps.development.graphql.interfaces import MilestoneOwner
from apps.development.graphql.resolvers import ProjectMilestonesResolver
from apps.development.graphql.types.milestone import MilestoneType
from apps.development.models import Project
from apps.development.services.issue.summary import IssuesProjectSummary


class ProjectType(BaseDjangoObjectType):
    """Project type."""

    class Meta:
        model = Project
        interfaces = (DatasourceRelayNode, MilestoneOwner)
        connection_class = DataSourceConnection
        name = "Project"

    milestones = DataSourceConnectionField(
        MilestoneType, filterset_class=MilestonesFilterSet,
    )

    def resolve_milestones(self: Project, info, **kwargs):  # noqa: WPS110
        """Get project milestones."""
        is_summary = isinstance(
            getattr(self, "parent_type", None), IssuesProjectSummary,
        )

        if is_summary:
            return self._handle_within_summary(**kwargs)

        resolver = ProjectMilestonesResolver(self, info, **kwargs)

        return resolver.execute()

    def _handle_within_summary(self, project: Project, **kwargs):
        """Handle project milestones within issues project summary."""
        ordering = kwargs.get("order_by")

        if ordering == "due_date":
            default = datetime.max.date()
            return sorted(
                project.active_milestones,
                key=lambda milestone: milestone.due_date or default,
            )
        elif ordering == "-due_date":
            default = datetime.min.date()
            return sorted(
                project.active_milestones,
                key=lambda milestone: milestone.due_date or default,
                reverse=True,
            )

        return project.active_milestones
