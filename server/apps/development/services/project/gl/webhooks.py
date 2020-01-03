# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.urls import reverse
from django.utils.functional import cached_property
from gitlab import GitlabError
from gitlab.v4 import objects as gl

from apps.development.models import Project
from apps.development.services.project.gl.provider import ProjectGlProvider

logger = logging.getLogger(__name__)


class ProjectWebhookManager:
    """Project webhook manager."""

    def __init__(self):
        """Initializing."""
        self.project_provider = ProjectGlProvider()

    @cached_property
    def webhook_url(self) -> str:
        """Get webhook url."""
        return "https://{domain}{path}".format(
            domain=settings.DOMAIN_NAME,
            path=reverse("api:gl-webhook"),
        )

    def check_project_webhooks(
        self,
        project: Project,
    ) -> None:
        """Check whether webhooks for project are needed."""
        if not settings.GITLAB_CHECK_WEBHOOKS:
            return

        gl_project = self.project_provider.get_gl_project(project)
        if not gl_project:
            return

        try:
            self._check_project_webhooks(gl_project)
        except GitlabError:
            logger.exception("Error on check project webhook")

    def _check_project_webhooks(self, gl_project: gl.Project) -> None:
        """Validate webhooks for project."""
        hooks = gl_project.hooks.list()

        tp_webhooks = [
            hook
            for hook in hooks
            if hook.url == self.webhook_url
        ]

        has_valid = self._check_webhooks(tp_webhooks)

        if not has_valid:
            gl_project.hooks.create({
                "url": self.webhook_url,
                "token": settings.GITLAB_WEBHOOK_SECRET_TOKEN,
                "issues_events": True,
                "merge_requests_events": True,
            })

    def _check_webhooks(self, tp_webhooks) -> bool:
        has_valid = False

        for webhook in tp_webhooks:
            if has_valid:
                webhook.delete()

            if self._validate_webhook(webhook, self.webhook_url):
                has_valid = True
            else:
                webhook.delete()

        return has_valid

    def _validate_webhook(self, webhook, webhook_url: str) -> bool:
        """Validate webhook."""
        return (
            webhook.url == webhook_url
            and webhook.issues_events
            and webhook.merge_requests_events
        )
