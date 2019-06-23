import json
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from apps.core.activity.verbs import ACTION_GITLAB_WEBHOOK_TRIGGERED
from apps.core.tasks import add_action
from ...tasks import sync_project_issue

logger = logging.getLogger(__name__)


@csrf_exempt
def gl_webhook(request):
    body = json.loads(request.body.decode('utf-8'))
    if body['object_kind'] != 'issue':
        return HttpResponse()

    project_id = body['project']['id']
    issue_id = body['object_attributes']['iid']

    sync_project_issue.delay(project_id, issue_id)

    logger.info(f'gitlab webhook was triggered: project_id = {project_id}, issue_id = {issue_id}')
    add_action.delay(verb=ACTION_GITLAB_WEBHOOK_TRIGGERED)

    return HttpResponse()
