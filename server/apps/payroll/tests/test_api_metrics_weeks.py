from datetime import datetime, timedelta
from typing import Dict

from django.db.models import Sum
from django.test import override_settings
from django.utils import timezone
from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.core.utils.date import next_weekday
from apps.development.tests.factories import IssueFactory
from apps.payroll.tests.factories import IssueSpentTimeFactory


@override_settings(TP_WEEKENDS_DAYS=[])
class ApiMetricsWeeksTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.issue = IssueFactory.create(employee=self.user, due_date=timezone.now())

    def test_simple(self):
        monday = next_weekday(timezone.now(), 0)

        self._create_spent_time(monday + timedelta(days=4), timedelta(hours=3))
        self._create_spent_time(monday + timedelta(days=2, hours=5), timedelta(hours=2))
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(monday + timedelta(days=1, hours=5), -timedelta(hours=3))

        self.issue.time_estimate = timedelta(hours=15).total_seconds()
        self.issue.total_time_spent = self.issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        self.issue.state = 'opened'
        self.issue.due_date = timezone.now() + timedelta(days=1)
        self.issue.save()

        self.set_credentials()
        start = monday - timedelta(days=5)
        end = monday + timedelta(days=5)

        response = self.client.get('/api/metrics', {
            'user': self.user.id,
            'start': self.format_date(start),
            'end': self.format_date(end),
            'group': 'week'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), (end - start).days + 1)

        self._check_metrics(response.data,
                            {
                                timezone.now() - timedelta(days=4): timedelta(hours=3),
                                timezone.now() - timedelta(days=2): timedelta(hours=2),
                                timezone.now() - timedelta(days=1): timedelta(hours=1),
                            }, {
                                timezone.now(): timedelta(hours=8),
                                timezone.now() + timedelta(days=1): timedelta(hours=1),
                            }, {
                                timezone.now() + timedelta(days=1): 1
                            }, {
                                timezone.now() + timedelta(days=1): timedelta(hours=15)
                            })

    def _create_spent_time(self, date, spent: timedelta = None, user=None, issue=None):
        return IssueSpentTimeFactory.create(date=date,
                                            employee=user or self.user,
                                            base=issue or self.issue,
                                            time_spent=spent.total_seconds())

    def _check_metrics(self, metrics,
                       spents: Dict[datetime, timedelta],
                       loadings: Dict[datetime, timedelta],
                       issues_counts: Dict[datetime, int],
                       time_estimates: Dict[datetime, timedelta]):

        spents = {
            self.format_date(d): time
            for d, time in spents.items()
        }

        loadings = {
            self.format_date(d): time
            for d, time in loadings.items()
        }

        time_estimates = {
            self.format_date(d): time
            for d, time in time_estimates.items()
        }

        issues_counts = {
            self.format_date(d): count
            for d, count in issues_counts.items()
        }

        for metric in metrics:
            self.assertEqual(metric['start'], metric['end'])

            if metric['start'] in spents:
                self.assertEqual(metric['time_spent'],
                                 spents[metric['start']].total_seconds(),
                                 f'bad spent for {metric["start"]}: '
                                 f'expected - {spents[metric["start"]]}, '
                                 f'actual - {timedelta(seconds=metric["time_spent"])}')
            else:
                self.assertEqual(metric['time_spent'], 0,
                                 f'bad spent for {metric["start"]}: '
                                 f'expected - 0, '
                                 f'actual - {timedelta(seconds=metric["time_spent"])}')

            if metric['start'] in time_estimates:
                self.assertEqual(metric['time_estimate'],
                                 time_estimates[metric['start']].total_seconds(),
                                 f'bad time_estimate for {metric["start"]}: '
                                 f'expected - {time_estimates[metric["start"]]}, '
                                 f'actual - {timedelta(seconds=metric["time_estimate"])}')
            else:
                self.assertEqual(metric['time_estimate'], 0,
                                 f'bad time_estimate for {metric["start"]}: '
                                 f'expected - 0, '
                                 f'actual - {timedelta(seconds=metric["time_estimate"])}')

            if metric['start'] in loadings:
                self.assertEqual(metric['loading'],
                                 loadings[metric['start']].total_seconds(),
                                 f'bad loading for {metric["start"]}: '
                                 f'expected - {loadings[metric["start"]]}, '
                                 f'actual - {timedelta(seconds=metric["loading"])}')
            else:
                self.assertEqual(metric['loading'], 0,
                                 f'bad loading for {metric["start"]}: '
                                 f'expected - 0, '
                                 f'actual - {timedelta(seconds=metric["loading"])}')

            if metric['start'] in issues_counts:
                self.assertEqual(metric['issues'], issues_counts[metric['start']])
            else:
                self.assertEqual(metric['issues'], 0)
