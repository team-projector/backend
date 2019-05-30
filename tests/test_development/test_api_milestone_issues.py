from rest_framework import status

from apps.users.models import User
from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory, ProjectGroupMilestoneFactory


class ApiMilestoneIssuesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.user.roles = User.roles.project_manager
        self.user.save()

        self.milestone = ProjectGroupMilestoneFactory.create()

    def test_empty_list(self):
        self.set_credentials()
        response = self.client.get(f'/api/milestones/{self.milestone.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_list(self):
        issue = IssueFactory.create(milestone=self.milestone)
        IssueFactory.create_batch(5)

        self.set_credentials()
        response = self.client.get(f'/api/milestones/{self.milestone.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)
        self.assertEqual(response.data['results'][0]['milestone']['id'], self.milestone.id)
