from datetime import date, timedelta
from typing import Dict

from django.db.models import Sum
from django.test import override_settings
from django.utils import timezone
from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.core.utils.date import begin_of_week
from apps.development.models import STATE_CLOSED, STATE_OPENED, TeamMember
from apps.development.tests.factories import IssueFactory, TeamFactory, TeamMemberFactory
from apps.development.utils.parsers import parse_date
from apps.payroll.tests.factories import IssueSpentTimeFactory
from apps.users.tests.factories import UserFactory


@override_settings(TP_WEEKENDS_DAYS=[])
class ApiMetricsWeeksTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.issue = IssueFactory.create(user=self.user, due_date=timezone.now())

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

        response = self.client.get(f'/api/users/{self.user.id}/progress-metrics', {
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

    def test_efficiency_more_1(self):
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

        response = self.client.get(f'/api/users/{self.user.id}/progress-metrics', {
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
                            }, {
                                monday: self.issue.time_estimate / self.issue.total_time_spent
                            })

    def test_efficiency_less_1(self):
        monday = begin_of_week(timezone.now().date())

        self._create_spent_time(monday + timedelta(days=4), timedelta(hours=3))
        self._create_spent_time(monday + timedelta(days=2, hours=5), timedelta(hours=2))
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(monday + timedelta(days=1, hours=5), -timedelta(hours=3))

        self.issue.time_estimate = timedelta(hours=3).total_seconds()
        self.issue.total_time_spent = self.issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        self.issue.state = STATE_CLOSED
        self.issue.due_date = monday + timedelta(days=1)
        self.issue.closed_at = monday + timedelta(days=1)
        self.issue.save()

        self.set_credentials()
        start = monday - timedelta(days=5)
        end = monday + timedelta(days=5)

        response = self.client.get(f'/api/users/{self.user.id}/progress-metrics', {
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
                                monday: timedelta(hours=3)
                            }, {
                                monday: self.issue.time_estimate / self.issue.total_time_spent
                            })

    def test_efficiency_zero_estimate(self):
        monday = begin_of_week(timezone.now().date())

        self._create_spent_time(monday + timedelta(days=4), timedelta(hours=3))
        self._create_spent_time(monday + timedelta(days=2, hours=5), timedelta(hours=2))
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(monday + timedelta(days=1, hours=5), -timedelta(hours=3))

        self.issue.time_estimate = 0
        self.issue.total_time_spent = self.issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        self.issue.state = STATE_CLOSED
        self.issue.due_date = monday + timedelta(days=1)
        self.issue.closed_at = monday + timedelta(days=1)
        self.issue.save()

        self.set_credentials()
        start = monday - timedelta(days=5)
        end = monday + timedelta(days=5)

        response = self.client.get(f'/api/users/{self.user.id}/progress-metrics', {
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
                            }, {}, {})

    def test_efficiency_zero_spend(self):
        monday = begin_of_week(timezone.now().date())

        self.issue.time_estimate = timedelta(hours=2).total_seconds()
        self.issue.total_time_spent = 0
        self.issue.state = STATE_CLOSED
        self.issue.due_date = monday + timedelta(days=1)
        self.issue.closed_at = monday + timedelta(days=1)
        self.issue.save()

        self.set_credentials()
        start = monday - timedelta(days=5)
        end = monday + timedelta(days=5)

        response = self.client.get(f'/api/users/{self.user.id}/progress-metrics', {
            'start': self.format_date(start),
            'end': self.format_date(end),
            'group': 'week'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        self._check_metrics(response.data,
                            {},
                            {
                                monday: 1
                            }, {
                                monday: timedelta(hours=2)
                            }, {})

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

        response = self.client.get(f'/api/users/{self.user.id}/progress-metrics', {
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

        response = self.client.get(f'/api/users/{self.user.id}/progress-metrics', {
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

        response = self.client.get(f'/api/users/{self.user.id}/progress-metrics', {
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
        another_issue = IssueFactory.create(user=self.user,
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

        response = self.client.get(f'/api/users/{self.user.id}/progress-metrics', {
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

    def test_permissions_self(self):
        self.set_credentials()
        response = self.client.get(f'/api/users/{self.user.id}/progress-metrics', {
            'start': self.format_date(timezone.now() - timedelta(days=5)),
            'end': self.format_date(timezone.now() - timedelta(days=5)),
            'group': 'week'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permissions_another_user(self):
        user_2 = self.create_user('user_2@mail.com')

        self.set_credentials()
        response = self.client.get(f'/api/users/{user_2.id}/progress-metrics', {
            'start': self.format_date(timezone.now() - timedelta(days=5)),
            'end': self.format_date(timezone.now() - timedelta(days=5)),
            'group': 'week'
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permissions_another_user_but_team_lead(self):
        user_2 = self.create_user('user_2@mail.com')

        team = TeamFactory.create()

        TeamMemberFactory.create(team=team,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team,
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        self.set_credentials()
        response = self.client.get(f'/api/users/{user_2.id}/progress-metrics', {
            'start': self.format_date(timezone.now() - timedelta(days=5)),
            'end': self.format_date(timezone.now() - timedelta(days=5)),
            'group': 'week'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permissions_another_user_but_another_team_lead(self):
        user_2 = self.create_user('user_2@mail.com')

        TeamMemberFactory.create(team=TeamFactory.create(),
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=TeamFactory.create(),
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        self.set_credentials()
        response = self.client.get(f'/api/users/{user_2.id}/progress-metrics', {
            'start': self.format_date(timezone.now() - timedelta(days=5)),
            'end': self.format_date(timezone.now() - timedelta(days=5)),
            'group': 'week'
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permissions_another_user_but_team_developer(self):
        user_2 = self.create_user('user_2@mail.com')

        self.set_credentials()
        response = self.client.get(f'/api/users/{user_2.id}/progress-metrics', {
            'start': self.format_date(timezone.now() - timedelta(days=5)),
            'end': self.format_date(timezone.now() - timedelta(days=5)),
            'group': 'week'
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _create_spent_time(self, date, spent: timedelta = None, user=None, issue=None):
        return IssueSpentTimeFactory.create(date=date,
                                            user=user or self.user,
                                            base=issue or self.issue,
                                            time_spent=spent.total_seconds())

    def _check_metrics(self, metrics,
                       spents: Dict[date, timedelta],
                       issues_counts: Dict[date, int],
                       time_estimates: Dict[date, timedelta],
                       efficiencies: Dict[date, float]):

        spents = self._prepare_metrics(spents)
        time_estimates = self._prepare_metrics(time_estimates)
        issues_counts = self._prepare_metrics(issues_counts)
        efficiencies = self._prepare_metrics(efficiencies)

        for metric in metrics:
            self.assertEqual(metric['end'], self.format_date(parse_date(metric['start']) + timedelta(weeks=1)))

            self._check_metric(metric, 'time_spent', spents)
            self._check_metric(metric, 'time_estimate', time_estimates)

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
