from datetime import timedelta

from rest_framework import status

from apps.development.models import STATE_OPENED
from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory, SalaryFactory


class ApiIssuesMetricsTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.user.hour_rate = 100
        self.user.save()

        self.issue = IssueFactory.create(user=self.user, state=STATE_OPENED)

    def test_payroll_metrics(self):
        self._create_spent_time(timedelta(hours=3))
        self._create_spent_time(timedelta(hours=2))
        self._create_spent_time(timedelta(hours=4))
        self._create_spent_time(-timedelta(hours=3))

        self.set_credentials()
        response = self.client.get('/api/issues', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        issue = response.data['results'][0]

        self.assertEqual(issue['metrics']['payroll'], 6 * self.user.hour_rate)
        self.assertEqual(issue['metrics']['paid'], 0)

    def test_paid_metrics(self):
        salary = SalaryFactory.create(user=self.user)

        self._create_spent_time(timedelta(hours=3), salary=salary)
        self._create_spent_time(timedelta(hours=2), salary=salary)
        self._create_spent_time(timedelta(hours=4), salary=salary)
        self._create_spent_time(-timedelta(hours=3), salary=salary)

        self.set_credentials()
        response = self.client.get('/api/issues', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        issue = response.data['results'][0]

        self.assertEqual(issue['metrics']['payroll'], 0)
        self.assertEqual(issue['metrics']['paid'], 6 * self.user.hour_rate)

    def test_complex_metrics(self):
        salary = SalaryFactory.create(user=self.user)

        self._create_spent_time(timedelta(hours=3), salary=salary)
        self._create_spent_time(timedelta(hours=2), salary=salary)
        self._create_spent_time(timedelta(hours=4))
        self._create_spent_time(-timedelta(hours=3))

        self.set_credentials()
        response = self.client.get('/api/issues', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        issue = response.data['results'][0]

        self.assertEqual(issue['metrics']['payroll'], self.user.hour_rate)
        self.assertEqual(issue['metrics']['paid'], 5 * self.user.hour_rate)

    def _create_spent_time(self, spent: timedelta = None, user=None, issue=None, salary=None):
        return IssueSpentTimeFactory.create(user=user or self.user,
                                            base=issue or self.issue,
                                            salary=salary,
                                            time_spent=spent.total_seconds())
