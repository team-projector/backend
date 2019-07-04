from rest_framework import status

from apps.users.models import User
from tests.base import BaseAPITest
from tests.test_development.factories import (FeatureFactory, IssueFactory)
from tests.test_payroll.factories import IssueSpentTimeFactory


class ApiFeatureIssuesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.user.roles = User.roles.project_manager
        self.user.save()

    def test_not_found(self):
        self.set_credentials()
        response = self.client.get('/api/features/1/issues')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_empty_list(self):
        feature = FeatureFactory.create()

        self.set_credentials()
        response = self.client.get(f'/api/features/{feature.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['count'])

    def test_list(self):
        feature = FeatureFactory.create()

        issue_1 = IssueFactory.create(feature=feature)
        issue_2 = IssueFactory.create(feature=feature)
        IssueFactory.create_batch(5)

        self.set_credentials()
        response = self.client.get(f'/api/features/{feature.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIn(issue_1.id, [x['id'] for x in response.data['results']])
        self.assertIn(issue_2.id, [x['id'] for x in response.data['results']])

    def test_issues_metrics(self):
        feature = FeatureFactory.create()

        issue = IssueFactory.create(feature=feature, time_estimate=4,
                                    total_time_spent=2)
        IssueSpentTimeFactory(user=self.user, base=issue, time_spent=5)

        self.set_credentials()
        response = self.client.get(f'/api/features/{feature.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)
        self.assertFalse(response.data['results'][0]['metrics'])

        response = self.client.get(f'/api/features/{feature.id}/issues', {
            'metrics': 'true'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertIsNotNone(response.data['results'][0]['metrics'])
        self.assertEqual(response.data['results'][0]['metrics']['remains'], 2)
        self.assertIsNone(response.data['results'][0]['metrics']['efficiency'])
        self.assertEqual(response.data['results'][0]['metrics']['payroll'], 0.0)
        self.assertEqual(response.data['results'][0]['metrics']['paid'], 0.0)

    def test_time_spent(self):
        feature = FeatureFactory.create()

        issue = IssueFactory.create(feature=feature)
        IssueSpentTimeFactory(user=self.user, base=issue, time_spent=5)

        self.set_credentials()
        response = self.client.get(f'/api/features/{feature.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)
        self.assertEqual(response.data['results'][0]['time_spent'], 5)
