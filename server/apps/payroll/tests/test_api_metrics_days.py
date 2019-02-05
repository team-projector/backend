from datetime import datetime, timedelta
from typing import Dict

from django.test import override_settings
from django.utils import timezone
from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.tests.factories import IssueFactory
from apps.payroll.tests.factories import IssueSpentTimeFactory
from apps.users.tests.factories import UserFactory


@override_settings(TP_WEEKENDS_DAYS=[])
class ApiMetricsDaysTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.issue = IssueFactory.create(employee=self.user, due_date=timezone.now())

    def test_simple(self):
        self.issue.time_estimate = timedelta(hours=10).total_seconds()
        self.issue.total_time_spent = timedelta(hours=1).total_seconds()
        self.issue.state = 'opened'
        self.issue.due_date = timezone.now() + timedelta(days=1)
        self.issue.save()

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

        self._check_metrics(response.data,
                            {
                                timezone.now() - timedelta(days=2): timedelta(hours=2),
                                timezone.now() - timedelta(days=1): timedelta(hours=1),
                                timezone.now() + timedelta(days=1): timedelta(hours=3)
                            }, {
                                timezone.now(): timedelta(hours=8),
                                timezone.now() + timedelta(days=1): timedelta(hours=1),
                            }, {
                                timezone.now() + timedelta(days=1): 1
                            })

    def test_not_in_range(self):
        self.issue.time_estimate = 0
        self.issue.total_time_spent = 0
        self.issue.state = 'opened'
        self.issue.save()

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

        self._check_metrics(response.data,
                            {
                                timezone.now() - timedelta(days=1): timedelta(hours=1),
                                timezone.now() + timedelta(days=1): timedelta(hours=3)
                            }, {}, {
                                timezone.now(): 1
                            })

    def test_another_user(self):
        self.issue.time_estimate = 0
        self.issue.total_time_spent = 0
        self.issue.state = 'opened'
        self.issue.save()

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

        self._check_metrics(response.data,
                            {
                                timezone.now() - timedelta(days=2): timedelta(hours=2),
                                timezone.now() - timedelta(days=1): -timedelta(hours=3)
                            }, {}, {
                                timezone.now(): 1
                            })

    def _create_spent_time(self, date, spent: timedelta = None, user=None):
        return IssueSpentTimeFactory.create(date=date,
                                            employee=user or self.user,
                                            base=self.issue,
                                            time_spent=spent.total_seconds())

    def _check_metrics(self, metrics,
                       spents: Dict[datetime, timedelta],
                       loadings: Dict[datetime, timedelta],
                       issues_counts: Dict[datetime, int]):

        spents = {
            self.format_date(d): time.total_seconds()
            for d, time in spents.items()
        }

        loadings = {
            self.format_date(d): time.total_seconds()
            for d, time in loadings.items()
        }

        issues_counts = {
            self.format_date(d): count
            for d, count in issues_counts.items()
        }

        for metric in metrics:
            self.assertEqual(metric['start'], metric['end'])

            if metric['start'] in spents:
                self.assertEqual(metric['time_spent'], spents[metric['start']])
            else:
                self.assertEqual(metric['time_spent'], 0)

            if metric['start'] in loadings:
                self.assertEqual(metric['loading'], loadings[metric['start']])
            else:
                self.assertEqual(metric['loading'], 0)

            if metric['start'] in issues_counts:
                self.assertEqual(metric['issues'], issues_counts[metric['start']])
            else:
                self.assertEqual(metric['issues'], 0)
