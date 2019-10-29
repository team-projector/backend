# -*- coding: utf-8 -*-

import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import AuthenticationFailed

from apps.core.activity.verbs import ACTION_GITLAB_WEBHOOK_TRIGGERED
from apps.core.tasks import add_action_task
from apps.development.tasks import (
    sync_project_issue_task,
    sync_project_merge_request_task,
)

logger = logging.getLogger(__name__)


@csrf_exempt
def gl_webhook(request):
    """Gitlab webhook."""
    _check_webhook_secret_token(
        request.META.get('HTTP_X_GITLAB_TOKEN'),
    )

    body = json.loads(request.body.decode('utf-8'))
    kind = body['object_kind']

    if kind == 'issue':
        _sync_issue(body)
    elif kind == 'merge_request':
        _sync_merge_request(body)

    return HttpResponse()


def _sync_issue(body: dict) -> None:
    project_id = body['project']['id']
    issue_id = body['object_attributes']['iid']

    sync_project_issue_task.delay(project_id, issue_id)

    logger.info(
        f'gitlab webhook was triggered: project_id = {project_id}, '
        + f'issue_id = {issue_id}',
    )

    add_action_task.delay(verb=ACTION_GITLAB_WEBHOOK_TRIGGERED)


def _sync_merge_request(body: dict) -> None:
    project_id = body['project']['id']
    issue_id = body['object_attributes']['iid']

    sync_project_merge_request_task.delay(project_id, issue_id)

    logger.info(
        f'gitlab webhook was triggered: project_id = {project_id}, '
        + f'merge_request_id = {issue_id}',
    )

    add_action_task.delay(verb=ACTION_GITLAB_WEBHOOK_TRIGGERED)


def _check_webhook_secret_token(secret_token: str) -> None:
    if not settings.WEBHOOK_SECRET_TOKEN:
        return

    if settings.WEBHOOK_SECRET_TOKEN != secret_token:
        raise AuthenticationFailed('Invalid token')
