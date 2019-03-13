from datetime import datetime, timedelta
from typing import Dict

from django.db.models import Sum
from django.test import override_settings
from django.utils import timezone
from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.models import STATE_OPENED
from apps.development.tests.factories import IssueFactory
from apps.payroll.tests.factories import IssueSpentTimeFactory
from apps.users.tests.factories import UserFactory


@override_settings(TP_WEEKENDS_DAYS=[])
class ApiMetricsDaysTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.issue = IssueFactory.create(employee=self.user, due_date=timezone.now())

    def test_bad_group(self):
        self.set_credentials()

        response = self.client.get(f'/api/users/{self.user.id}/metrics', {
            'start': timezone.now() - timedelta(days=5),
            'end': timezone.now() + timedelta(days=5),
            'group': 'days'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_simple(self):
        self._create_spent_time(timezone.now() - timedelta(days=4), timedelta(hours=3))
        self._create_spent_time(timezone.now() - timedelta(days=2, hours=5), timedelta(hours=2))
        self._create_spent_time(timezone.now() - timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(timezone.now() - timedelta(days=1, hours=5), -timedelta(hours=3))

        self.issue.time_estimate = timedelta(hours=15).total_seconds()
        self.issue.total_time_spent = self.issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        self.issue.state = STATE_OPENED
        self.issue.due_date = timezone.now() + timedelta(days=1)
        self.issue.save()

        self.set_credentials()
        start = timezone.now() - timedelta(days=5)
        end = timezone.now() + timedelta(days=5)

        response = self.client.get(f'/api/users/{self.user.id}/metrics', {
            'start': self.format_date(start),
            'end': self.format_date(end),
            'group': 'day'
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
                            }, {
                                timezone.now() + timedelta(days=1):
                                    timedelta(seconds=self.issue.time_estimate - self.issue.total_time_spent)
                            })

    def test_negative_remains(self):
        self._create_spent_time(timezone.now() - timedelta(days=4), timedelta(hours=3))

        self.issue.time_estimate = timedelta(hours=2).total_seconds()
        self.issue.total_time_spent = self.issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        self.issue.state = STATE_OPENED
        self.issue.due_date = timezone.now() + timedelta(days=1)
        self.issue.save()

        self.set_credentials()
        start = timezone.now() - timedelta(days=5)
        end = timezone.now() + timedelta(days=5)

        response = self.client.get(f'/api/users/{self.user.id}/metrics', {
            'start': self.format_date(start),
            'end': self.format_date(end),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), (end - start).days + 1)

        self._check_metrics(response.data,
                            {
                                timezone.now() - timedelta(days=4): timedelta(hours=3),
                            }, {}, {
                                timezone.now() + timedelta(days=1): 1
                            }, {
                                timezone.now() + timedelta(days=1): timedelta(hours=2)
                            }, {})

    def test_loading_day_already_has_spends(self):
        issue_2 = IssueFactory.create(employee=self.user,
                                      state=STATE_OPENED,
                                      total_time_spent=timedelta(hours=3).total_seconds(),
                                      time_estimate=timedelta(hours=10).total_seconds())

        self._create_spent_time(timezone.now(), timedelta(hours=1), issue=issue_2)
        self._create_spent_time(timezone.now(), timedelta(hours=2), issue=issue_2)
        self._create_spent_time(timezone.now(), timedelta(hours=3))

        self.issue.time_estimate = int(timedelta(hours=4).total_seconds())
        self.issue.total_time_spent = int(timedelta(hours=3).total_seconds())
        self.issue.state = STATE_OPENED
        self.issue.due_date = timezone.now()
        self.issue.save()

        issue_2.total_time_spent = issue_2.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        issue_2.save()

        self.set_credentials()
        start = timezone.now() - timedelta(days=5)
        end = timezone.now() + timedelta(days=5)

        response = self.client.get(f'/api/users/{self.user.id}/metrics', {
            'start': self.format_date(start),
            'end': self.format_date(end),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), (end - start).days + 1)

        self._check_metrics(response.data,
                            {
                                timezone.now(): timedelta(hours=6)
                            }, {
                                timezone.now(): timedelta(hours=8),
                                timezone.now() + timedelta(days=1): timedelta(hours=6),
                            }, {
                                timezone.now(): 1,
                            }, {
                                timezone.now(): timedelta(hours=4),
                            }, {
                                timezone.now(): timedelta(
                                    seconds=self.issue.time_estimate - self.issue.total_time_spent)
                            })

    def test_not_in_range(self):
        self.issue.time_estimate = 0
        self.issue.total_time_spent = 0
        self.issue.state = STATE_OPENED
        self.issue.save()

        self._create_spent_time(timezone.now() - timedelta(days=5, hours=5), timedelta(hours=2))
        self._create_spent_time(timezone.now() - timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(timezone.now() - timedelta(days=1, hours=5), -timedelta(hours=3))
        self._create_spent_time(timezone.now() + timedelta(days=1), timedelta(hours=3))

        start = timezone.now() - timedelta(days=3)
        end = timezone.now() + timedelta(days=3)

        self.set_credentials()
        response = self.client.get(f'/api/users/{self.user.id}/metrics', {
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
                            }, {}, {})

    def test_another_user(self):
        self.issue.time_estimate = 0
        self.issue.total_time_spent = 0
        self.issue.state = STATE_OPENED
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
        response = self.client.get(f'/api/users/{self.user.id}/metrics', {
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
                            }, {}, {})

    def _create_spent_time(self, date, spent: timedelta = None, user=None, issue=None):
        return IssueSpentTimeFactory.create(date=date,
                                            employee=user or self.user,
                                            base=issue or self.issue,
                                            time_spent=spent.total_seconds())

    def _check_metrics(self, metrics,
                       spents: Dict[datetime, timedelta],
                       loadings: Dict[datetime, timedelta],
                       issues_counts: Dict[datetime, int],
                       time_estimates: Dict[datetime, timedelta],
                       time_remains: Dict[datetime, timedelta]):
        spents = self._prepare_metrics(spents)
        loadings = self._prepare_metrics(loadings)
        time_estimates = self._prepare_metrics(time_estimates)
        issues_counts = self._prepare_metrics(issues_counts)
        time_remains = self._prepare_metrics(time_remains)

        for metric in metrics:
            self.assertEqual(metric['start'], metric['end'])

            self._check_metric(metric, 'time_spent', spents)
            self._check_metric(metric, 'time_estimate', time_estimates)
            self._check_metric(metric, 'loading', loadings)
            self._check_metric(metric, 'time_remains', time_remains)

            if metric['start'] in issues_counts:
                self.assertEqual(metric['issues_count'], issues_counts[metric['start']])
            else:
                self.assertEqual(metric['issues_count'], 0)

    def _prepare_metrics(self, metrics):
        return {
            self.format_date(d): time
            for d, time in metrics.items()
        }

    def _check_metric(self, metric, metric_name, values):
        if metric['start'] in values:
            self.assertEqual(metric[metric_name],
                             values[metric['start']].total_seconds(),
                             f'bad {metric_name} for {metric["start"]}: '
                             f'expected - {values[metric["start"]]}, '
                             f'actual - {timedelta(seconds=metric[metric_name])}')
        else:
            self.assertEqual(metric[metric_name],
                             0,
                             f'bad {metric_name} for {metric["start"]}: '
                             f'expected - 0, '
                             f'actual - {timedelta(seconds=metric[metric_name])}')
