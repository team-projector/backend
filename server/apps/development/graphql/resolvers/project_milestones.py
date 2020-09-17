# -*- coding: utf-8 -*-

from datetime import datetime

from apps.development.graphql.resolvers import ProjectMilestonesResolver
from apps.development.models import Project
from apps.development.services.issue.summary import IssuesProjectSummary


def resolve_project_milestones(
    project: Project,
    info,  # noqa: WPS110
    **kwargs,
):
    """Get project milestones."""
    is_summary = isinstance(
        getattr(project, "parent_type", None),
        IssuesProjectSummary,
    )

    if is_summary and isinstance(project, Project):
        return _handle_within_summary(project, **kwargs)

    resolver = ProjectMilestonesResolver(project, info, **kwargs)

    return resolver.execute()


def _handle_within_summary(project: Project, **kwargs):
    """Handle project milestones within issues project summary."""
    ordering = kwargs.get("order_by")

    if ordering not in {"due_date", "-due_date"}:
        return project.active_milestones

    return sorted(
        project.active_milestones,
        key=lambda milestone: milestone.due_date or datetime.max.date(),
        reverse=ordering == "-due_date",
    )
