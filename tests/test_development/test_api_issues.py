from rest_framework import status

from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory
from tests.test_users.factories import UserFactory


class ApiIssuesTests(BaseAPITest):
    def test_list(self):
        IssueFactory.create_batch(5, user=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_show_participants(self):
        user = UserFactory.create()
        issue = IssueFactory.create(user=user)

        users = UserFactory.create_batch(size=3)
        issue.participants.set(users)

        self.set_credentials()
        response = self.client.get('/api/issues', {'user': user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(set(x['id'] for x in response.data['results'][0]['participants']),
                         set(x.id for x in users))
