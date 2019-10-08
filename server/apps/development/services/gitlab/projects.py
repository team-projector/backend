# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.urls import reverse
from gitlab import Gitlab, GitlabError, GitlabGetError
from gitlab.v4.objects import Project as GlProject
from rest_framework import status

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action

from ...models import Project, ProjectGroup

logger = logging.getLogger(__name__)


def load_projects() -> None:
    """Load all projects."""
    for group in ProjectGroup.objects.all():
        load_group_projects(group)


def load_group_projects(group: ProjectGroup) -> None:
    """Load projects for group."""
    gl = get_gitlab_client()

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    try:
        gl_group = gl.groups.get(id=group.gl_id)
    except GitlabGetError as error:
        if error.response_code != status.HTTP_404_NOT_FOUND:
            raise
    else:
        for gl_project in gl_group.projects.list(all=True):
            load_project(gl, group, gl_project)


def load_project(
    gl: Gitlab,
    group: ProjectGroup,
    gl_project: GlProject,
) -> None:
    """Load project."""
    msg = f'Syncing project "{gl_project.name}"...'

    logger.info(f'{msg}')

    try:
        Project.objects.sync_gitlab(
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
        check_project_webhooks_if_need(gl, gl_project)

    logger.info(f'{msg} done')


def check_project_webhooks_if_need(
    gl: Gitlab,
    gl_project: GlProject,
):
    """Check whether webhooks for project are needed."""
    if not settings.GITLAB_CHECK_WEBHOOKS:
        return

    try:
        check_project_webhooks(gl.projects.get(gl_project.id))
    except GitlabError as error:
        logger.exception(str(error))


def check_project_webhooks(gl_project: GlProject) -> None:
    """Validate webhooks for project."""
    hooks = gl_project.hooks.list()

    webhook_url = f'https://{settings.DOMAIN_NAME}{reverse("api:gl-webhook")}'

    tp_webhooks = [
        hook
        for hook in hooks
        if hook.url == webhook_url
    ]

    has_valid = False

    for webhook in tp_webhooks:
        if has_valid:
            webhook.delete()

        if validate_webhook(webhook, webhook_url):
            has_valid = True
        else:
            webhook.delete()

    if not has_valid:
        gl_project.hooks.create({
            'url': webhook_url,
            'token': settings.WEBHOOK_SECRET_TOKEN,
            'issues_events': True,
            'merge_requests_events': True,
        })


def validate_webhook(
    webhook,
    webhook_url: str,
) -> bool:
    """Validate webhook."""
    return (
        webhook.url == webhook_url
        and webhook.issues_events
        and webhook.merge_requests_events
    )
