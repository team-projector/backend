from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.tests.factories import IssueFactory
from apps.users.tests.factories import UserFactory


class ApiUserMetrcisTests(BaseAPITest):
    def test_retrieve(self):
        user = UserFactory.create()

        IssueFactory.create_batch(10, user=user)

        self.set_credentials()
        response = self.client.get(f'/api/users/{user.id}', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertIsNotNone(response.data['metrics'])
        self.assertEqual(response.data['metrics']['issues_opened_count'], 10)

    def test_no_metrics(self):
        user = UserFactory.create()

        self.set_credentials()
        response = self.client.get(f'/api/users/{user.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertIsNone(response.data['metrics'])

    def test_me(self):
        IssueFactory.create_batch(10, user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/me/user', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertIsNotNone(response.data['metrics'])
        self.assertIsNotNone(response.data['metrics']['issues_opened_count'], 10)
