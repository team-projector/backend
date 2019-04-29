from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from apps.core.activity.verbs import ACTION_GITLAB_WEBHOOK_TRIGGERED, ACTION_GITLAB_CALL_API
from apps.core.tasks import add_action
from apps.development.models import Issue, Project
from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory


class GitlabStatusTests(BaseAPITest):
    def test_status(self):
        IssueFactory.create_batch(size=20)
        Issue.objects.update(updated_at=timezone.now())

        project = Project.objects.first()
        project.gl_last_sync = timezone.now() + timedelta(minutes=2)
        project.save()

        add_action.delay(sender_id=self.user.id, verb=ACTION_GITLAB_WEBHOOK_TRIGGERED)
        add_action.delay(sender_id=self.user.id, verb=ACTION_GITLAB_CALL_API)

        self.set_credentials()

        response = self.client.get('/api/gitlab/status')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['last_sync'], project.gl_last_sync)
        self.assertEqual(
            set(x['id'] for x in response.data['last_issues']),
            set(Issue.objects.order_by('-updated_at')[:10].values_list('id', flat=True))
        )
