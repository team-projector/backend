import json

from django.utils import dateparse
from django.views.decorators.csrf import csrf_exempt
from requests import Response

from apps.development.models import Issue, Project
from apps.users.models import User

@csrf_exempt
def gl_webhook(request):
    body = json.loads(request.body.decode('utf-8'))

    if body['object_kind'] != 'issue':
        return Response()

    project_data = body['project']
    project, _ = Project.objects.sync_gitlab(gl_id=project_data['id'],
                                             gl_url=project_data['web_url'],
                                             title=project_data['name'])

    issue_data = body['object_attributes']

    employee = None
    if issue_data['assignee_id']:
        employee = User.objects.filter(gl_id=issue_data['assignee_id']).first()

    issue, _ = Issue.objects.sync_gitlab(gl_id=issue_data['id'],
                                         project=project,
                                         title=issue_data['title'],
                                         total_time_spent=issue_data['total_time_spent'],
                                         time_estimate=issue_data['time_estimate'],
                                         state=issue_data['state'],
                                         gl_url=issue_data['url'],
                                         employee=employee)

    return Response()
