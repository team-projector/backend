import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from apps.development.tasks import sync_project_issue


@csrf_exempt
def gl_webhook(request):
    body = json.loads(request.body.decode('utf-8'))
    if body['object_kind'] != 'issue':
        return HttpResponse()

    sync_project_issue.delay(body['project']['id'], body['object_attributes']['iid'])

    return HttpResponse()
