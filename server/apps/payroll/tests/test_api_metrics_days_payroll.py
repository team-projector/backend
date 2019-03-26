from datetime import date, timedelta
from typing import Dict

from django.test import override_settings
from django.utils import timezone
from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.core.utils.date import begin_of_week
from apps.development.models import STATE_CLOSED, STATE_OPENED
from apps.development.tests.factories import IssueFactory
from apps.payroll.tests.factories import IssueSpentTimeFactory, SalaryFactory


@override_settings(TP_WEEKENDS_DAYS=[])
class ApiMetricsDaysPayrollTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.user.hour_rate = 100
        self.user.save()

        self.issue = IssueFactory.create(user=self.user, due_date=timezone.now())

    def test_opened(self):
        monday = begin_of_week(timezone.now().date())

        self._create_spent_time(monday, timedelta(hours=3))
        self._create_spent_time(monday + timedelta(days=2, hours=5), timedelta(hours=2))
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(monday + timedelta(days=1, hours=5), -timedelta(hours=3))
        self._create_spent_time(monday + timedelta(days=10), -timedelta(hours=3))

        self.issue.state = STATE_OPENED
        self.issue.save()

        self.set_credentials()
        start = monday - timedelta(days=5)
        end = monday + timedelta(days=5)

        response = self.client.get(f'/api/users/{self.user.id}/progress-metrics', {
            'start': self.format_date(start),
            'end': self.format_date(end),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._check_metrics(response.data,
                            {
                                monday: 0
                            }, {
                                monday: 3 * self.user.hour_rate,
                                monday + timedelta(days=1): self.user.hour_rate,
                                monday + timedelta(days=2): 2 * self.user.hour_rate
                            }, {
                                monday: 0
                            })

    def test_paid(self):
        monday = begin_of_week(timezone.now().date())

        salary = SalaryFactory.create(user=self.user)

        self._create_spent_time(monday, timedelta(hours=3), salary=salary)
        self._create_spent_time(monday + timedelta(days=2, hours=5), timedelta(hours=2), salary=salary)
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4), salary=salary)
        self._create_spent_time(monday + timedelta(days=1, hours=5), -timedelta(hours=3), salary=salary)
        self._create_spent_time(monday + timedelta(days=10), -timedelta(hours=3), salary=salary)

        self.issue.state = STATE_CLOSED
        self.issue.save()

        self.set_credentials()
        start = monday - timedelta(days=5)
        end = monday + timedelta(days=5)

        response = self.client.get(f'/api/users/{self.user.id}/progress-metrics', {
            'start': self.format_date(start),
            'end': self.format_date(end),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._check_metrics(response.data,
                            {
                                monday: 0
                            }, {
                                monday: 0
                            }, {
                                monday: 3 * self.user.hour_rate,
                                monday + timedelta(days=1): self.user.hour_rate,
                                monday + timedelta(days=2): 2 * self.user.hour_rate
                            })

    def test_closed(self):
        monday = begin_of_week(timezone.now().date())

        self._create_spent_time(monday, timedelta(hours=3))
        self._create_spent_time(monday + timedelta(days=2, hours=5), timedelta(hours=2))
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(monday + timedelta(days=1, hours=5), -timedelta(hours=3))
        self._create_spent_time(monday + timedelta(days=10), -timedelta(hours=3))

        self.issue.state = STATE_CLOSED
        self.issue.save()

        self.set_credentials()
        start = monday - timedelta(days=5)
        end = monday + timedelta(days=5)

        response = self.client.get(f'/api/users/{self.user.id}/progress-metrics', {
            'start': self.format_date(start),
            'end': self.format_date(end),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._check_metrics(response.data,
                            {
                                monday: 3 * self.user.hour_rate,
                                monday + timedelta(days=1): self.user.hour_rate,
                                monday + timedelta(days=2): 2 * self.user.hour_rate
                            }, {
                                monday: 0
                            }, {
                                monday: 0
                            })

    def test_complex(self):
        monday = begin_of_week(timezone.now().date())

        salary = SalaryFactory.create(user=self.user)

        closed_issue = IssueFactory.create(user=self.user, due_date=timezone.now(), state=STATE_CLOSED)
        opened_issue = IssueFactory.create(user=self.user, due_date=timezone.now(), state=STATE_OPENED)

        self._create_spent_time(monday, timedelta(hours=4), issue=closed_issue)
        self._create_spent_time(monday, timedelta(hours=2), issue=opened_issue)
        self._create_spent_time(monday + timedelta(days=2, hours=5), timedelta(hours=2), issue=opened_issue)
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4), issue=opened_issue)
        self._create_spent_time(monday + timedelta(days=1, hours=5),
                                timedelta(hours=3),
                                salary=salary,
                                issue=closed_issue)
        self._create_spent_time(monday + timedelta(days=10), -timedelta(hours=3),
                                issue=opened_issue)

        self.set_credentials()
        start = monday - timedelta(days=5)
        end = monday + timedelta(days=5)

        response = self.client.get(f'/api/users/{self.user.id}/progress-metrics', {
            'start': self.format_date(start),
            'end': self.format_date(end),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._check_metrics(response.data,
                            {
                                monday: 4 * self.user.hour_rate,
                            }, {
                                monday: 2 * self.user.hour_rate,
                                monday + timedelta(days=1): 4 * self.user.hour_rate,
                                monday + timedelta(days=2): 2 * self.user.hour_rate,
                            }, {
                                monday + timedelta(days=1): 3 * self.user.hour_rate,
                            })

    def _create_spent_time(self, date, spent: timedelta = None, user=None, issue=None, salary=None):
        return IssueSpentTimeFactory.create(date=date,
                                            user=user or self.user,
                                            base=issue or self.issue,
                                            salary=salary,
                                            time_spent=spent.total_seconds())

    def _check_metrics(self, metrics,
                       payroll_closed: Dict[date, float],
                       payroll_opened: Dict[date, float],
                       paid: Dict[date, float]):

        payroll_closed = self._prepare_metrics(payroll_closed)
        payroll_opened = self._prepare_metrics(payroll_opened)
        paid = self._prepare_metrics(paid)

        for metric in metrics:
            self.assertEqual(metric['start'], metric['end'])

            self._check_metric(metric, 'payroll_closed', payroll_closed)
            self._check_metric(metric, 'payroll_opened', payroll_opened)
            self._check_metric(metric, 'paid', paid)

    def _prepare_metrics(self, metrics):
        return {
            self.format_date(d): time
            for d, time in metrics.items()
        }

    def _check_metric(self, metric, metric_name, values):
        if metric['start'] in values:
            self.assertEqual(metric[metric_name],
                             values[metric['start']],
                             f'bad {metric_name} for {metric["start"]}: '
                             f'expected - {values[metric["start"]]}, '
                             f'actual - {metric[metric_name]}')
        else:
            self.assertEqual(metric[metric_name],
                             0,
                             f'bad {metric_name} for {metric["start"]}: '
                             f'expected - 0, '
                             f'actual - {metric[metric_name]}')
