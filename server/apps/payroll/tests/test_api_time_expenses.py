from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.tests.factories import IssueFactory
from apps.payroll.tests.factories import IssueSpentTimeFactory


class ApiTimeExpensesTests(BaseAPITest):
    def test_list(self):
        issue = IssueFactory.create()

        spend_1 = IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=4),
                                               employee=self.user,
                                               base=issue,
                                               time_spent=int(timedelta(hours=5).total_seconds()))

        spend_2 = IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=2),
                                               employee=self.user,
                                               base=issue,
                                               time_spent=int(timedelta(hours=2).total_seconds()))

        spend_3 = IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=3),
                                               employee=self.user,
                                               base=issue,
                                               time_spent=int(timedelta(hours=4).total_seconds()))

        spend_4 = IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=1),
                                               employee=self.user,
                                               base=issue,
                                               time_spent=int(timedelta(minutes=10).total_seconds()))

        self.set_credentials()
        response = self.client.get('/api/time-expenses')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_time_expences(response.data, [spend_1, spend_2, spend_3, spend_4])

    def _check_time_expences(self, data, spends):
        self.assertEqual(len(data), len(spends))

        for i, spend in enumerate(spends):
            data['id'] = spend.id
            data['date'] = spend.date
            data['issue']['id'] = spend.content_object.id
            data['time_spent'] = spend.time_spent
