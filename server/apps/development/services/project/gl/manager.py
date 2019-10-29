# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.urls import reverse
from django.utils.functional import cached_property
from gitlab import GitlabError
from gitlab.v4.objects import Project as GlProject

from apps.development.models import Project, ProjectGroup
from apps.development.services.project.gl.provider import ProjectGlProvider
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

    @cached_property
    def webhook_url(self) -> str:
        """Get webhook url."""
        return f'https://{settings.DOMAIN_NAME}{reverse("api:gl-webhook")}'

    def sync_all_projects(self) -> None:
        """Sync all projects."""
        for group in ProjectGroup.objects.all():
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
        gl_project: GlProject,
    ) -> None:
        """Update project based on gitlab data."""
        msg = f'Updating project "{gl_project.name}"...'

        logger.info(f'{msg}')

        try:
            Project.objects.update_from_gitlab(
                gl_id=gl_project.id,
                gl_url=gl_project.web_url,
                gl_avatar=gl_project.avatar_url,
                group=group,
                full_title=gl_project.name_with_namespace,
                title=gl_project.name,
            )
        except Exception as error:
            logger.exception(str(error))
        else:
            self._check_project_webhooks_if_need(gl_project)

        logger.info(f'{msg} done')

    def _check_project_webhooks_if_need(
        self,
        gl_project: GlProject,
    ) -> None:
        """Check whether webhooks for project are needed."""
        if not settings.GITLAB_CHECK_WEBHOOKS:
            return

        try:
            self._check_project_webhooks(gl_project)
        except GitlabError as error:
            logger.exception(str(error))

    def _check_project_webhooks(
        self,
        gl_project: GlProject,
    ) -> None:
        """Validate webhooks for project."""
        hooks = gl_project.hooks.list()

        tp_webhooks = [
            hook
            for hook in hooks
            if hook.url == self.webhook_url
        ]

        has_valid = False

        for webhook in tp_webhooks:
            if has_valid:
                webhook.delete()

            if self._validate_webhook(webhook, self.webhook_url):
                has_valid = True
            else:
                webhook.delete()

        if not has_valid:
            gl_project.hooks.create({
                'url': self.webhook_url,
                'token': settings.WEBHOOK_SECRET_TOKEN,
                'issues_events': True,
                'merge_requests_events': True,
            })

    def _validate_webhook(
        self,
        webhook,
        webhook_url: str,
    ) -> bool:
        """Validate webhook."""
        return (
            webhook.url == webhook_url
            and webhook.issues_events
            and webhook.merge_requests_events
        )
