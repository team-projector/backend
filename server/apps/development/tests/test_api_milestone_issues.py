from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.tests.factories import ProjectGroupMilestoneFactory, IssueFactory


class ApiMilestoneIssuesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.milestone = ProjectGroupMilestoneFactory.create()

    def test_empty_list(self):
        self.set_credentials()
        response = self.client.get(f'/api/milestones/{self.milestone.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_list(self):
        issue = IssueFactory.create(issue_milestone=self.milestone)
        IssueFactory.create_batch(5)

        self.set_credentials()
        response = self.client.get(f'/api/milestones/{self.milestone.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)
        self.assertEqual(response.data['results'][0]['milestone']['id'], self.milestone.id)
