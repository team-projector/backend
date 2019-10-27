# -*- coding: utf-8 -*-

import logging

from django.utils import timezone
from gitlab import GitlabGetError
from rest_framework import status

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action
from apps.development.models import Project
from apps.development.services.issue.gitlab.checkers import (
    check_project_deleted_issues,
)
from apps.development.services.issue.gitlab.issue import load_for_project

logger = logging.getLogger(__name__)


def load_issues(full_reload: bool = False) -> None:
    """Load issues for all projects."""
    for project in Project.objects.all():
        try:
            load_for_project_all(project, full_reload)
        except GitlabGetError as error:
            if error.response_code != status.HTTP_404_NOT_FOUND:
                raise


def load_for_project_all(
    project: Project,
    full_reload: bool = False,
    check_deleted: bool = True,
) -> None:
    """Load project issues."""
    gl = get_gitlab_client()

    logger.info(f'Syncing project "{project}" issues')
    gl_project = gl.projects.get(id=project.gl_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    args = {
        'as_list': False,
    }

    if not full_reload and project.gl_last_issues_sync:
        args['updated_after'] = project.gl_last_issues_sync

    project.gl_last_issues_sync = timezone.now()
    project.save(update_fields=['gl_last_issues_sync'])

    for gl_issue in gl_project.issues.list(**args):
        load_for_project(project, gl_project, gl_issue)

    if check_deleted:
        check_project_deleted_issues(project, gl_project)
