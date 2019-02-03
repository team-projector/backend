from datetime import datetime, timedelta
from typing import Dict

from django.utils import timezone
from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.tests.factories import IssueFactory
from apps.payroll.tests.factories import IssueSpentTimeFactory
from apps.users.tests.factories import UserFactory


class ApiMetricsDaysTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.issue = IssueFactory.create()

    def test_simple(self):
        self._create_spent_time(timezone.now() - timedelta(days=2, hours=5), timedelta(hours=2))
        self._create_spent_time(timezone.now() - timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(timezone.now() - timedelta(days=1, hours=5), -timedelta(hours=3))
        self._create_spent_time(timezone.now() + timedelta(days=1), timedelta(hours=3))

        self.set_credentials()
        start = timezone.now() - timedelta(days=5)
        end = timezone.now() + timedelta(days=5)

        response = self.client.get('/api/metrics', {
            'user': self.user.id,
            'start': self.format_date(start),
            'end': self.format_date(end),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), (end - start).days + 1)

        self._check_metrics(response.data, {
            timezone.now() - timedelta(days=2): timedelta(hours=2),
            timezone.now() - timedelta(days=1): timedelta(hours=1),
            timezone.now() + timedelta(days=1): timedelta(hours=3)
        })

    def test_not_in_range(self):
        self._create_spent_time(timezone.now() - timedelta(days=5, hours=5), timedelta(hours=2))
        self._create_spent_time(timezone.now() - timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(timezone.now() - timedelta(days=1, hours=5), -timedelta(hours=3))
        self._create_spent_time(timezone.now() + timedelta(days=1), timedelta(hours=3))

        start = timezone.now() - timedelta(days=3)
        end = timezone.now() + timedelta(days=3)

        self.set_credentials()
        response = self.client.get('/api/metrics', {
            'user': self.user.id,
            'start': self.format_date(start),
            'end': self.format_date(end),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), (end - start).days + 1)

        self._check_metrics(response.data, {
            timezone.now() - timedelta(days=1): timedelta(hours=1),
            timezone.now() + timedelta(days=1): timedelta(hours=3)
        })

    def test_another_user(self):
        another_user = UserFactory.create()

        self._create_spent_time(timezone.now() - timedelta(days=2, hours=5), timedelta(hours=2))
        self._create_spent_time(timezone.now() - timedelta(days=1), timedelta(hours=4),
                                user=another_user)
        self._create_spent_time(timezone.now() - timedelta(days=1, hours=5), -timedelta(hours=3))
        self._create_spent_time(timezone.now() + timedelta(days=1), timedelta(hours=3), user=another_user)

        start = timezone.now() - timedelta(days=5)
        end = timezone.now() + timedelta(days=5)

        self.set_credentials()
        response = self.client.get('/api/metrics', {
            'user': self.user.id,
            'start': self.format_date(start),
            'end': self.format_date(end),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), (end - start).days + 1)

        self._check_metrics(response.data, {
            timezone.now() - timedelta(days=2): timedelta(hours=2),
            timezone.now() - timedelta(days=1): -timedelta(hours=3)
        })

    def _create_spent_time(self, date, spent: timedelta = None, user=None):
        return IssueSpentTimeFactory.create(date=date,
                                            employee=user or self.user,
                                            base=self.issue,
                                            time_spent=spent.total_seconds())

    def _check_metrics(self, metrics, spents: Dict[datetime, timedelta]):
        for metric in metrics:
            if metric['start'] in spents:
                self._check_metric(metric, metric['start'], spents[metric['start']])

    def _check_metric(self, metric, day: datetime, spent: timedelta):
        self.assertEqual(metric['start'], metric['end'])
        self.assertEqual(metric['end'], self.format_date(day))
        self.assertEqual(metric['time_spent'], spent.total_seconds())
