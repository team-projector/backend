from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.tests.factories import IssueFactory
from apps.payroll.tests.factories import IssueSpentTimeFactory
from apps.users.tests.factories import UserFactory


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

    def test_filter_by_user(self):
        user_2 = UserFactory.create()

        issue = IssueFactory.create()

        IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=4),
                                     employee=self.user,
                                     base=issue,
                                     time_spent=int(timedelta(hours=5).total_seconds()))

        spend_2 = IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=2),
                                               employee=user_2,
                                               base=issue,
                                               time_spent=int(timedelta(hours=2).total_seconds()))

        IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=3),
                                     employee=self.user,
                                     base=issue,
                                     time_spent=int(timedelta(hours=4).total_seconds()))

        spend_4 = IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=1),
                                               employee=user_2,
                                               base=issue,
                                               time_spent=int(timedelta(minutes=10).total_seconds()))

        self.set_credentials()
        response = self.client.get('/api/time-expenses', {
            'employee': user_2.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_time_expences(response.data, [spend_2, spend_4])

    def test_filter_by_date(self):
        issue = IssueFactory.create()

        IssueSpentTimeFactory.create(date=timezone.now() - timedelta(weeks=1, hours=1),
                                     employee=self.user,
                                     base=issue,
                                     time_spent=int(timedelta(hours=5).total_seconds()))

        spend_2 = IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=2),
                                               employee=self.user,
                                               base=issue,
                                               time_spent=int(timedelta(hours=2).total_seconds()))

        IssueSpentTimeFactory.create(date=timezone.now() - timedelta(days=1, hours=1),
                                     employee=self.user,
                                     base=issue,
                                     time_spent=int(timedelta(hours=4).total_seconds()))

        spend_4 = IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=1),
                                               employee=self.user,
                                               base=issue,
                                               time_spent=int(timedelta(minutes=10).total_seconds()))

        self.set_credentials()
        response = self.client.get('/api/time-expenses', {
            'date': self.format_date(timezone.now())
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_time_expences(response.data, [spend_2, spend_4])

    def _check_time_expences(self, data, spends):
        self.assertEqual(data['count'], len(spends))

        for i, spend in enumerate(spends):
            expense = data['results'][i]

            expense['id'] = spend.id
            expense['date'] = spend.date
            expense['issue']['id'] = spend.base.id
            expense['time_spent'] = spend.time_spent
            expense['earnings'] = spend.earnings
