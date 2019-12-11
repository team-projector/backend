# -*- coding: utf-8 -*-

import logging

from django.db import DatabaseError
from gitlab.v4 import objects as gl

from apps.development.models import Project, ProjectGroup
from apps.development.services.project.gl.provider import ProjectGlProvider
from apps.development.services.project.gl.webhooks import ProjectWebhookManager
from apps.development.services.project_group.gl.provider import (
    ProjectGroupGlProvider,
)

logger = logging.getLogger(__name__)


class ProjectGlManager:
    """Project gitlab manager."""

    def __init__(self):
        """Initializing."""
        self.project_provider = ProjectGlProvider()
        self.group_provider = ProjectGroupGlProvider()
        self.webhook_manager = ProjectWebhookManager()

    def sync_all_projects(self) -> None:
        """Sync all projects."""
        for group in ProjectGroup.objects.for_sync():
            self.sync_group_projects(group)

    def sync_group_projects(
        self,
        group: ProjectGroup,
    ) -> None:
        """Sync projects of the group."""
        gl_group = self.group_provider.get_gl_group(group)
        if not gl_group:
            return

        for gl_project in gl_group.projects.list(all=True):
            self.update_project(group, gl_project)

    def update_project(
        self,
        group: ProjectGroup,
        gl_project: gl.Project,
    ) -> None:
        """Update project based on gitlab data."""
        msg = 'Updating project "{0}"...'.format(gl_project.name)

        logger.info(msg)

        try:
            project, _ = Project.objects.update_from_gitlab(
                gl_id=gl_project.id,
                gl_url=gl_project.web_url or '',
                gl_avatar=gl_project.avatar_url or '',
                group=group,
                full_title=gl_project.name_with_namespace,
                title=gl_project.name,
                is_archived=gl_project.archived,
            )
        except DatabaseError:
            logger.exception('Error on update project from gitlab')
        else:
            self.webhook_manager.check_project_webhooks(project)

        logger.info('{0} done'.format(msg))
