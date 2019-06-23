import logging

from django.conf import settings
from django.urls import reverse
from gitlab import Gitlab, GitlabGetError
from gitlab.v4.objects import Project as GlProject
from rest_framework import status

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action
from ...models import Project, ProjectGroup

logger = logging.getLogger(__name__)


def load_projects() -> None:
    for group in ProjectGroup.objects.all():
        load_group_projects(group)


def load_group_projects(group: ProjectGroup) -> None:
    gl = get_gitlab_client()

    try:
        gl_group = gl.groups.get(id=group.gl_id)
        add_action.delay(verb=ACTION_GITLAB_CALL_API)
    except GitlabGetError as e:
        if e.response_code != status.HTTP_404_NOT_FOUND:
            raise
    else:
        for gl_project in gl_group.projects.list(all=True):
            load_project(gl, group, gl_project)


def load_project(gl: Gitlab,
                 group: ProjectGroup,
                 gl_project: GlProject) -> None:
    msg = f'Syncing project "{gl_project.name}"...'

    try:
        project, _ = Project.objects.sync_gitlab(
            gl_id=gl_project.id,
            gl_url=gl_project.web_url,
            group=group,
            full_title=gl_project.name_with_namespace,
            title=gl_project.name
        )

        if settings.GITLAB_CHECK_WEBHOOKS:
            check_project_webhooks(gl.projects.get(gl_project.id))
    except Exception as e:
        logger.info(f'{msg}')
        logger.exception(str(e))
    else:
        logger.info(f'{msg} done')


def check_project_webhooks(gl_project: GlProject) -> None:
    hooks = gl_project.hooks.list()

    webhook_url = f'https://{settings.DOMAIN_NAME}{reverse("api:gl-webhook")}'

    if any(hook.url == webhook_url for hook in hooks):
        return

    gl_project.hooks.create({
        'url': webhook_url,
        'issues_events': True
    })
