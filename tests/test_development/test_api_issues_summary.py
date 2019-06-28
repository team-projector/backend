from rest_framework import status

from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory
from tests.test_users.factories import UserFactory


class ApiIssuesSummaryTests(BaseAPITest):
    def test_one_user(self):
        IssueFactory.create_batch(5, user=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues/summary', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._check_summary(response.data, 5, 0, 0)

    def test_filter_by_user(self):
        IssueFactory.create_batch(5, user=self.user)

        another_user = UserFactory.create()
        IssueFactory.create_batch(5, user=another_user)

        self.set_credentials()
        response = self.client.get('/api/issues/summary', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_summary(response.data, 5, 0, 0)

    def _check_summary(self, data, issues_count, time_spent, problems_count):
        self.assertEqual(data['issues_count'], issues_count)
        self.assertEqual(data['time_spent'], time_spent)
        self.assertEqual(data['problems_count'], problems_count)
