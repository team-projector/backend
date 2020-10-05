# -*- coding: utf-8 -*-

import logging

from django.db import DatabaseError
from django.utils import timezone
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
        for group in ProjectGroup.objects.filter(is_active=True):
            self.sync_group_projects(group)

    def sync_group_projects(self, group: ProjectGroup) -> None:
        """Sync projects of the group."""
        gl_group = self.group_provider.get_gl_group(group)
        if not gl_group:
            return

        for gl_project in gl_group.projects.list(all=True):
            shared_with_groups = getattr(gl_project, "shared_with_groups", [])
            is_shared = any(
                shared_group["group_id"] == gl_group.id
                for shared_group in shared_with_groups
            )
            if not is_shared:
                self.update_project(group, gl_project)

    def update_project(
        self,
        group: ProjectGroup,
        gl_project: gl.Project,
    ) -> None:
        """Update project based on gitlab data."""
        msg = "Updating project '{0}'...".format(gl_project.name)

        logger.info(msg)
        fields = {
            "gl_url": gl_project.web_url,
            "gl_avatar": gl_project.avatar_url or "",
            "group": group,
            "full_title": gl_project.name_with_namespace,
            "title": gl_project.name,
            "is_archived": gl_project.archived,
            "gl_last_sync": timezone.now(),
        }
        try:

            project, _ = Project.objects.update_or_create(
                gl_id=gl_project.id,
                defaults=fields,
            )
        except (DatabaseError, ValueError):
            logger.exception("Error on update project from gitlab")
        else:
            self.webhook_manager.check_project_webhooks(project)

        logger.info("{0} done".format(msg))
