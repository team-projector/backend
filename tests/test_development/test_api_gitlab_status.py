from datetime import timedelta

import dateutil.parser
from django.utils import timezone
from rest_framework import status

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API, ACTION_GITLAB_WEBHOOK_TRIGGERED
from apps.core.tasks import add_action
from apps.development.models import Issue, Project
from tests.test_development.factories import IssueFactory


def test_status(user, api_client):
    IssueFactory.create_batch(size=20)
    Issue.objects.update(updated_at=timezone.now())

    project = Project.objects.first()
    project.gl_last_sync = timezone.now() + timedelta(minutes=2)
    project.save()

    add_action.delay(sender_id=user.id, verb=ACTION_GITLAB_WEBHOOK_TRIGGERED)
    add_action.delay(sender_id=user.id, verb=ACTION_GITLAB_CALL_API)

    api_client.set_credentials(user)
    response = api_client.get('/api/gitlab/status')

    assert response.status_code == status.HTTP_200_OK

    assert dateutil.parser.parse(response.data['last_sync']) == \
           project.gl_last_sync
    assert set(x['id'] for x in response.data['last_issues']) == \
           set(Issue.objects.order_by('-updated_at')[:10].values_list('id', flat=True))
