from rest_framework import status

from apps.users.models import User
from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory, FeatureFactory, ProjectGroupMilestoneFactory


class ApiMilestoneIssuesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.user.roles = User.roles.project_manager
        self.user.save()

        self.milestone = ProjectGroupMilestoneFactory.create()

    def test_list_not_found(self):
        self.set_credentials()
        response = self.client.get(f'/api/milestones/{self.milestone.id + 1}/issues/orphan')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_empty(self):
        self.set_credentials()
        response = self.client.get(f'/api/milestones/{self.milestone.id}/issues/orphan')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_list(self):
        issue = IssueFactory.create(milestone=self.milestone)

        feature = FeatureFactory.create(milestone=self.milestone)
        IssueFactory.create_batch(5, milestone=self.milestone, feature=feature)
        IssueFactory.create_batch(5)

        self.set_credentials()
        response = self.client.get(f'/api/milestones/{self.milestone.id}/issues/orphan')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)
        self.assertEqual(response.data['results'][0]['title'], issue.title)
        self.assertEqual(response.data['results'][0]['milestone']['id'], self.milestone.id)
        self.assertFalse(response.data['results'][0]['feature'])

    def test_list_with_metrics(self):
        IssueFactory.create_batch(5, milestone=self.milestone)

        self.set_credentials()
        response = self.client.get(f'/api/milestones/{self.milestone.id}/issues/orphan', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)
        self.assertTrue(all(item['metrics'] is not None for item in response.data['results']))
