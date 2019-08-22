import json
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from apps.core.activity.verbs import ACTION_GITLAB_WEBHOOK_TRIGGERED
from apps.core.tasks import add_action
from ...tasks import sync_project_issue, sync_project_merge_request

logger = logging.getLogger(__name__)


@csrf_exempt
def gl_webhook(request):
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

    sync_project_issue.delay(project_id, issue_id)

    logger.info(f'gitlab webhook was triggered: '
                f'project_id = {project_id}, issue_id = {issue_id}')
    add_action.delay(verb=ACTION_GITLAB_WEBHOOK_TRIGGERED)


def _sync_merge_request(body: dict) -> None:
    project_id = body['project']['id']
    issue_id = body['object_attributes']['iid']

    sync_project_merge_request.delay(project_id, issue_id)

    logger.info(f'gitlab webhook was triggered: '
                f'project_id = {project_id}, merge_request_id = {issue_id}')
    add_action.delay(verb=ACTION_GITLAB_WEBHOOK_TRIGGERED)
