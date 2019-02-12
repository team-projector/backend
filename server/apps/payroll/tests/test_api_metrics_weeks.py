from datetime import date, timedelta
from typing import Dict

from django.db.models import Sum
from django.test import override_settings
from django.utils import timezone
from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.core.utils.date import begin_of_week
from apps.development.models import STATE_OPENED, STATE_CLOSED
from apps.development.tests.factories import IssueFactory
from apps.development.utils.parsers import parse_date
from apps.payroll.tests.factories import IssueSpentTimeFactory
from apps.users.tests.factories import UserFactory


@override_settings(TP_WEEKENDS_DAYS=[])
class ApiMetricsWeeksTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.issue = IssueFactory.create(employee=self.user, due_date=timezone.now())

    def test_simple(self):
        monday = begin_of_week(timezone.now().date())

        self._create_spent_time(monday + timedelta(days=4), timedelta(hours=3))
        self._create_spent_time(monday + timedelta(days=2, hours=5), timedelta(hours=2))
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(monday + timedelta(days=1, hours=5), -timedelta(hours=3))

        self.issue.time_estimate = timedelta(hours=15).total_seconds()
        self.issue.total_time_spent = self.issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        self.issue.state = STATE_OPENED
        self.issue.due_date = monday + timedelta(days=1)
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
        self.assertEqual(len(response.data), 2)

        self._check_metrics(response.data,
                            {
                                monday: timedelta(hours=6)
                            }, {
                                monday: 1
                            }, {
                                monday: timedelta(hours=15)
                            }, {})

    def test_efficiency(self):
        monday = begin_of_week(timezone.now().date())

        self._create_spent_time(monday + timedelta(days=4), timedelta(hours=3))
        self._create_spent_time(monday + timedelta(days=2, hours=5), timedelta(hours=2))
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(monday + timedelta(days=1, hours=5), -timedelta(hours=3))

        self.issue.time_estimate = timedelta(hours=15).total_seconds()
        self.issue.total_time_spent = self.issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        self.issue.state = STATE_CLOSED
        self.issue.due_date = monday + timedelta(days=1)
        self.issue.closed_at = monday + timedelta(days=1)
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
        self.assertEqual(len(response.data), 2)

        self._check_metrics(response.data,
                            {
                                monday: timedelta(hours=6)
                            }, {}, {}, {
                                monday: self.issue.total_time_spent / self.issue.time_estimate
                            })

    def test_many_weeks(self):
        monday = begin_of_week(timezone.now().date())

        self._create_spent_time(monday - timedelta(days=4), timedelta(hours=3))
        self._create_spent_time(monday - timedelta(days=2, hours=5), timedelta(hours=2))
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(monday + timedelta(days=1, hours=5), -timedelta(hours=3))

        self.issue.time_estimate = timedelta(hours=15).total_seconds()
        self.issue.total_time_spent = self.issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        self.issue.state = STATE_OPENED
        self.issue.due_date = monday + timedelta(days=2)
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
        self.assertEqual(len(response.data), 2)

        self._check_metrics(response.data,
                            {
                                monday - timedelta(weeks=1): timedelta(hours=5),
                                monday: timedelta(hours=1)
                            }, {
                                monday: 1
                            }, {
                                monday: timedelta(hours=15)
                            }, {})

    def test_not_in_range(self):
        monday = begin_of_week(timezone.now().date())

        self._create_spent_time(monday - timedelta(days=4), timedelta(hours=3))
        self._create_spent_time(monday - timedelta(days=2, hours=5), timedelta(hours=2))
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(monday + timedelta(days=1, hours=5), -timedelta(hours=3))

        self.issue.time_estimate = timedelta(hours=15).total_seconds()
        self.issue.total_time_spent = self.issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        self.issue.state = STATE_OPENED
        self.issue.due_date = monday + timedelta(days=1)
        self.issue.save()

        self.set_credentials()
        start = monday
        end = monday + timedelta(weeks=1, days=5)

        response = self.client.get('/api/metrics', {
            'user': self.user.id,
            'start': self.format_date(start),
            'end': self.format_date(end),
            'group': 'week'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        self._check_metrics(response.data,
                            {
                                monday: timedelta(hours=1)
                            }, {
                                monday: 1
                            }, {
                                monday: timedelta(hours=15)
                            }, {})

    def test_another_user(self):
        another_user = UserFactory.create()

        monday = begin_of_week(timezone.now().date())

        self._create_spent_time(monday + timedelta(days=4), timedelta(hours=3))
        self._create_spent_time(monday + timedelta(days=2, hours=5), timedelta(hours=2))
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4), user=another_user)
        self._create_spent_time(monday + timedelta(days=1, hours=5), -timedelta(hours=3), user=another_user)

        self.issue.time_estimate = timedelta(hours=15).total_seconds()
        self.issue.total_time_spent = self.issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        self.issue.state = STATE_OPENED
        self.issue.due_date = monday + timedelta(days=1)
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
        self.assertEqual(len(response.data), 2)

        self._check_metrics(response.data,
                            {
                                monday: timedelta(hours=5)
                            }, {
                                monday: 1
                            }, {
                                monday: timedelta(hours=15)
                            }, {})

    def test_many_issues(self):
        monday = begin_of_week(timezone.now().date())
        another_issue = IssueFactory.create(employee=self.user,
                                            state=STATE_OPENED,
                                            due_date=monday + timedelta(days=4),
                                            total_time_spent=timedelta(hours=3).total_seconds(),
                                            time_estimate=timedelta(hours=10).total_seconds())

        self._create_spent_time(monday + timedelta(days=4), timedelta(hours=3), issue=another_issue)
        self._create_spent_time(monday + timedelta(days=2, hours=5), timedelta(hours=2), issue=another_issue)
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(monday + timedelta(days=1, hours=5), -timedelta(hours=3))

        self.issue.time_estimate = timedelta(hours=15).total_seconds()
        self.issue.total_time_spent = self.issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        self.issue.state = STATE_OPENED
        self.issue.due_date = monday + timedelta(days=1)
        self.issue.save()

        another_issue.total_time_spent = another_issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        another_issue.save()

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
        self.assertEqual(len(response.data), 2)

        self._check_metrics(response.data,
                            {
                                monday: timedelta(hours=6)
                            }, {
                                monday: 2
                            }, {
                                monday: timedelta(days=1, hours=1)
                            }, {})

    def _create_spent_time(self, date, spent: timedelta = None, user=None, issue=None):
        return IssueSpentTimeFactory.create(date=date,
                                            employee=user or self.user,
                                            base=issue or self.issue,
                                            time_spent=spent.total_seconds())

    def _check_metrics(self, metrics,
                       spents: Dict[date, timedelta],
                       issues_counts: Dict[date, int],
                       time_estimates: Dict[date, timedelta],
                       efficiencies: Dict[date, float]):

        spents = {
            self.format_date(d): time
            for d, time in spents.items()
        }

        time_estimates = {
            self.format_date(d): time
            for d, time in time_estimates.items()
        }

        issues_counts = {
            self.format_date(d): count
            for d, count in issues_counts.items()
        }

        efficiencies = {
            self.format_date(d): ef
            for d, ef in efficiencies.items()
        }

        for metric in metrics:
            self.assertEqual(metric['end'], self.format_date(parse_date(metric['start']) + timedelta(weeks=1)))

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

            if metric['start'] in efficiencies:
                self.assertEqual(metric['efficiency'],
                                 efficiencies[metric['start']],
                                 f'bad efficiency for {metric["start"]}: '
                                 f'expected - {efficiencies[metric["start"]]}, '
                                 f'actual - {metric["efficiency"]}')
            else:
                self.assertEqual(metric['efficiency'], 0,
                                 f'bad efficiency for {metric["start"]}: '
                                 f'expected - 0, '
                                 f'actual - {metric["efficiency"]}')

            if metric['start'] in issues_counts:
                self.assertEqual(metric['issues'], issues_counts[metric['start']])
            else:
                self.assertEqual(metric['issues'], 0)
