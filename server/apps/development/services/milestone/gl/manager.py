# -*- coding: utf-8 -*-

from typing import Dict, Union

from django.utils import timezone

from apps.core.gitlab.parsers import parse_gl_date, parse_gl_datetime
from apps.development.models import Milestone, Project, ProjectGroup
from apps.development.services.project.gl.provider import ProjectGlProvider
from apps.development.services.project_group.gl.provider import (
    ProjectGroupGlProvider,
)


class MilestoneGlManager:
    """Milestones gitlab manager."""

    def __init__(self):
        """Initializing."""
        self.project_provider = ProjectGlProvider()
        self.group_provider = ProjectGroupGlProvider()

    def sync_project_group_milestones(self, group: ProjectGroup) -> None:
        """Sync milestones for group."""
        gl_group = self.group_provider.get_gl_group(group)
        if not gl_group:
            return

        for gl_milestone in gl_group.milestones.list():
            self._update_milestone(
                gl_milestone,
                group,
            )

    def sync_project_group_milestone(
        self,
        group: ProjectGroup,
        gl_milestone_id: int,
    ) -> None:
        """Load milestone for group."""
        gl_group = self.group_provider.get_gl_group(group)
        if not gl_group:
            return

        self._update_milestone(
            gl_group.milestones.get(gl_milestone_id),
            group,
        )

    def sync_project_milestones(self, project: Project) -> None:
        """Sync milestones for project."""
        gl_project = self.project_provider.get_gl_project(project)
        if not gl_project:
            return

        for gl_milestone in gl_project.milestones.list():
            self._update_milestone(
                gl_milestone,
                project,
            )

    def sync_project_milestone(
        self,
        project: Project,
        gl_milestone_id: int,
    ) -> None:
        """Load milestone for project."""
        gl_project = self.project_provider.get_gl_project(project)
        if not gl_project:
            return

        self._update_milestone(
            gl_project.milestones.get(gl_milestone_id),
            project,
        )

    def _update_milestone(
        self,
        gl_milestone,
        owner: Union[ProjectGroup, Project],
    ) -> None:
        """
        Update milestone.

        :param gl_milestone:
        :param owner:
        :type owner: Union[ProjectGroup, Project]
        :rtype: None
        """
        fields = self._build_parameters(gl_milestone)
        fields["owner"] = owner
        Milestone.objects.update_or_create(
            gl_id=gl_milestone.id,
            defaults=fields,
        )

    def _build_parameters(self, gl_milestone) -> Dict[str, object]:
        """
        Build parameters.

        :param gl_milestone:
        :rtype: Dict[str, object]
        """
        return {
            "gl_iid": gl_milestone.iid,
            "gl_url": gl_milestone.web_url,
            "title": gl_milestone.title,
            "description": gl_milestone.description,
            "start_date": parse_gl_date(gl_milestone.start_date),
            "due_date": parse_gl_date(gl_milestone.due_date),
            "created_at": parse_gl_datetime(gl_milestone.created_at),
            "updated_at": parse_gl_datetime(gl_milestone.updated_at),
            "state": gl_milestone.state.upper(),
            "gl_last_sync": timezone.now(),
        }
