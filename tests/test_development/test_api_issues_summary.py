from rest_framework import status

from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory
from tests.test_users.factories import UserFactory


class ApiIssuesSummaryTests(BaseAPITest):
    def test_one_user(self):
        IssueFactory.create_batch(5, user=self.user, total_time_spent=0)

        self.set_credentials()
        response = self.client.get('/api/issues/summary', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._check_summary(response.data, 5, 0, 0)

    def test_filter_by_user(self):
        IssueFactory.create_batch(5, user=self.user, total_time_spent=0)

        another_user = UserFactory.create()
        IssueFactory.create_batch(5, user=another_user, total_time_spent=0)

        self.set_credentials()
        response = self.client.get('/api/issues/summary', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_summary(response.data, 5, 0, 0)

    def test_time_spents(self):
        issues = IssueFactory.create_batch(5, user=self.user)
        IssueFactory.create_batch(5, user=UserFactory.create())

        self.set_credentials()
        response = self.client.get('/api/issues/summary', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._check_summary(
            response.data,
            5,
            sum(issue.total_time_spent for issue in issues),
            0
        )

    def _check_summary(self, data, issues_count, time_spent, problems_count):
        self.assertEqual(issues_count, data['issues_count'])
        self.assertEqual(time_spent, data['time_spent'])
        self.assertEqual(problems_count, data['problems_count'])
