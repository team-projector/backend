from datetime import date, timedelta, datetime
from typing import Dict

from django.db.models import Sum
from django.test import override_settings
from django.utils import timezone
from rest_framework import status

from apps.core.utils.date import begin_of_week
from apps.development.models import TeamMember
from apps.development.models.issue import STATE_CLOSED, STATE_OPENED
from apps.development.services.parsers import parse_date
from tests.base import BaseAPITest, format_date
from tests.test_development.factories import (
    IssueFactory, TeamFactory, TeamMemberFactory
)
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories import UserFactory


@override_settings(TP_WEEKENDS_DAYS=[])
class ApiMetricsWeeksTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.developer = UserFactory.create()
        self.issue = IssueFactory.create(user=self.developer,
                                         due_date=datetime.now())

        self.team = TeamFactory.create()
        TeamMemberFactory.create(team=self.team, user=self.developer,
                                 roles=TeamMember.roles.developer)
        TeamMemberFactory.create(team=self.team, user=self.user,
                                 roles=TeamMember.roles.leader)

    def test_simple(self):
        monday = begin_of_week(timezone.now().date())

        self._create_spent_time(monday + timedelta(days=4), timedelta(hours=3))
        self._create_spent_time(monday + timedelta(days=2, hours=5),
                                timedelta(hours=2))
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(monday + timedelta(days=1, hours=5),
                                -timedelta(hours=3))

        self.issue.time_estimate = timedelta(hours=15).total_seconds()
        self.issue.total_time_spent = \
            self.issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        self.issue.state = STATE_OPENED
        self.issue.due_date = monday + timedelta(days=1)
        self.issue.save()

        self.set_credentials()
        start = monday - timedelta(days=5)
        end = monday + timedelta(days=5)

        response = self.client.get(
            f'/api/teams/{self.team.id}/progress-metrics', {
                'start': format_date(start),
                'end': format_date(end),
                'group': 'week'
            })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        developer_metrics = next(
            item for item in response.data if item['user'] == self.developer.id)

        self.assertEqual(developer_metrics['user'], self.developer.id)
        self.assertEqual(len(developer_metrics['metrics']), 2)

        self._check_metrics(developer_metrics['metrics'],
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
        self._create_spent_time(monday + timedelta(days=2, hours=5),
                                timedelta(hours=2))
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(monday + timedelta(days=1, hours=5),
                                -timedelta(hours=3))

        self.issue.time_estimate = timedelta(hours=15).total_seconds()
        self.issue.total_time_spent = self.issue.time_spents.aggregate(
            spent=Sum('time_spent')
        )['spent']
        self.issue.state = STATE_CLOSED
        self.issue.due_date = monday + timedelta(days=1)
        self.issue.closed_at = monday + timedelta(days=1)
        self.issue.save()

        self.set_credentials()
        start = monday - timedelta(days=5)
        end = monday + timedelta(days=5)

        response = self.client.get(
            f'/api/teams/{self.team.id}/progress-metrics', {
                'start': format_date(start),
                'end': format_date(end),
                'group': 'week'
            })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        developer_metrics = next(
            item for item in response.data if item['user'] == self.developer.id)

        self.assertEqual(developer_metrics['user'], self.developer.id)
        self.assertEqual(len(developer_metrics['metrics']), 2)

        self._check_metrics(developer_metrics['metrics'],
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
        self._create_spent_time(monday + timedelta(days=2, hours=5),
                                timedelta(hours=2))
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(monday + timedelta(days=1, hours=5),
                                -timedelta(hours=3))

        self.issue.time_estimate = timedelta(hours=3).total_seconds()
        self.issue.total_time_spent = self.issue.time_spents.aggregate(
            spent=Sum('time_spent')
        )['spent']
        self.issue.state = STATE_CLOSED
        self.issue.due_date = monday + timedelta(days=1)
        self.issue.closed_at = monday + timedelta(days=1)
        self.issue.save()

        self.set_credentials()
        start = monday - timedelta(days=5)
        end = monday + timedelta(days=5)

        response = self.client.get(
            f'/api/teams/{self.team.id}/progress-metrics', {
                'start': format_date(start),
                'end': format_date(end),
                'group': 'week'
            })

        developer_metrics = next(
            item for item in response.data if item['user'] == self.developer.id)

        self.assertEqual(developer_metrics['user'], self.developer.id)
        self.assertEqual(len(developer_metrics['metrics']), 2)

        self._check_metrics(developer_metrics['metrics'],
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
        self._create_spent_time(monday + timedelta(days=2, hours=5),
                                timedelta(hours=2))
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(monday + timedelta(days=1, hours=5),
                                -timedelta(hours=3))

        self.issue.time_estimate = 0
        self.issue.total_time_spent = \
            self.issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        self.issue.state = STATE_CLOSED
        self.issue.due_date = monday + timedelta(days=1)
        self.issue.closed_at = monday + timedelta(days=1)
        self.issue.save()

        self.set_credentials()
        start = monday - timedelta(days=5)
        end = monday + timedelta(days=5)

        response = self.client.get(
            f'/api/teams/{self.team.id}/progress-metrics', {
                'start': format_date(start),
                'end': format_date(end),
                'group': 'week'
            })

        developer_metrics = next(
            item for item in response.data if item['user'] == self.developer.id)

        self.assertEqual(developer_metrics['user'], self.developer.id)
        self.assertEqual(len(developer_metrics['metrics']), 2)

        self._check_metrics(developer_metrics['metrics'],
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

        response = self.client.get(
            f'/api/teams/{self.team.id}/progress-metrics', {
                'start': format_date(start),
                'end': format_date(end),
                'group': 'week'
            })

        developer_metrics = next(
            item for item in response.data if item['user'] == self.developer.id)

        self.assertEqual(developer_metrics['user'], self.developer.id)
        self.assertEqual(len(developer_metrics['metrics']), 2)

        self._check_metrics(developer_metrics['metrics'],
                            {},
                            {
                                monday: 1
                            }, {
                                monday: timedelta(hours=2)
                            }, {})

    def test_many_weeks(self):
        monday = begin_of_week(timezone.now().date())

        self._create_spent_time(monday - timedelta(days=4), timedelta(hours=3))
        self._create_spent_time(monday - timedelta(days=2, hours=5),
                                timedelta(hours=2))
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(monday + timedelta(days=1, hours=5),
                                -timedelta(hours=3))

        self.issue.time_estimate = timedelta(hours=15).total_seconds()
        self.issue.total_time_spent = \
            self.issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        self.issue.state = STATE_OPENED
        self.issue.due_date = monday + timedelta(days=2)
        self.issue.save()

        self.set_credentials()
        start = monday - timedelta(days=5)
        end = monday + timedelta(days=5)

        response = self.client.get(
            f'/api/teams/{self.team.id}/progress-metrics', {
                'start': format_date(start),
                'end': format_date(end),
                'group': 'week'
            })

        developer_metrics = next(
            item for item in response.data if item['user'] == self.developer.id)

        self.assertEqual(developer_metrics['user'], self.developer.id)
        self.assertEqual(len(developer_metrics['metrics']), 2)

        self._check_metrics(developer_metrics['metrics'],
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
        self._create_spent_time(monday - timedelta(days=2, hours=5),
                                timedelta(hours=2))
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(monday + timedelta(days=1, hours=5),
                                -timedelta(hours=3))

        self.issue.time_estimate = timedelta(hours=15).total_seconds()
        self.issue.total_time_spent = \
            self.issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        self.issue.state = STATE_OPENED
        self.issue.due_date = monday + timedelta(days=1)
        self.issue.save()

        self.set_credentials()
        start = monday
        end = monday + timedelta(weeks=1, days=5)

        response = self.client.get(
            f'/api/teams/{self.team.id}/progress-metrics', {
                'start': format_date(start),
                'end': format_date(end),
                'group': 'week'
            })

        developer_metrics = next(
            item for item in response.data if item['user'] == self.developer.id)

        self.assertEqual(developer_metrics['user'], self.developer.id)
        self.assertEqual(len(developer_metrics['metrics']), 2)

        self._check_metrics(developer_metrics['metrics'],
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
        self._create_spent_time(monday + timedelta(days=2, hours=5),
                                timedelta(hours=2))
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4),
                                user=another_user)
        self._create_spent_time(monday + timedelta(days=1, hours=5),
                                -timedelta(hours=3), user=another_user)

        self.issue.time_estimate = timedelta(hours=15).total_seconds()
        self.issue.total_time_spent = \
            self.issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        self.issue.state = STATE_OPENED
        self.issue.due_date = monday + timedelta(days=1)
        self.issue.save()

        self.set_credentials()
        start = monday - timedelta(days=5)
        end = monday + timedelta(days=5)

        response = self.client.get(
            f'/api/teams/{self.team.id}/progress-metrics', {
                'start': format_date(start),
                'end': format_date(end),
                'group': 'week'
            })

        developer_metrics = next(
            item for item in response.data if item['user'] == self.developer.id)

        self.assertEqual(developer_metrics['user'], self.developer.id)
        self.assertEqual(len(developer_metrics['metrics']), 2)

        self._check_metrics(developer_metrics['metrics'],
                            {
                                monday: timedelta(hours=5)
                            }, {
                                monday: 1
                            }, {
                                monday: timedelta(hours=15)
                            }, {})

    def test_many_issues(self):
        monday = begin_of_week(datetime.now().date())
        another_issue = IssueFactory.create(user=self.developer,
                                            state=STATE_OPENED,
                                            due_date=monday + timedelta(days=4),
                                            total_time_spent=timedelta(
                                                hours=3).total_seconds(),
                                            time_estimate=timedelta(
                                                hours=10).total_seconds())

        self._create_spent_time(monday + timedelta(days=4), timedelta(hours=3),
                                issue=another_issue)
        self._create_spent_time(monday + timedelta(days=2, hours=5),
                                timedelta(hours=2), issue=another_issue)
        self._create_spent_time(monday + timedelta(days=1), timedelta(hours=4))
        self._create_spent_time(monday + timedelta(days=1, hours=5),
                                -timedelta(hours=3))

        self.issue.time_estimate = timedelta(hours=15).total_seconds()
        self.issue.total_time_spent = \
            self.issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
        self.issue.state = STATE_OPENED
        self.issue.due_date = monday + timedelta(days=1)
        self.issue.save()

        another_issue.total_time_spent = \
            another_issue.time_spents.aggregate(spent=Sum('time_spent'))[
                'spent']
        another_issue.save()

        self.set_credentials()
        start = monday - timedelta(days=5)
        end = monday + timedelta(days=5)

        response = self.client.get(
            f'/api/teams/{self.team.id}/progress-metrics', {
                'start': format_date(start),
                'end': format_date(end),
                'group': 'week'
            })

        developer_metrics = next(
            item for item in response.data if item['user'] == self.developer.id)

        self.assertEqual(developer_metrics['user'], self.developer.id)
        self.assertEqual(len(developer_metrics['metrics']), 2)

        self._check_metrics(developer_metrics['metrics'],
                            {
                                monday: timedelta(hours=6)
                            }, {
                                monday: 2
                            }, {
                                monday: timedelta(days=1, hours=1)
                            }, {})

    def test_permissions_self(self):
        self.set_credentials()
        response = self.client.get(
            f'/api/teams/{self.team.id}/progress-metrics', {
                'start': format_date(timezone.now() - timedelta(days=5)),
                'end': format_date(timezone.now() - timedelta(days=5)),
                'group': 'week'
            })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permissions_another_user(self):
        user_2 = self.create_user('user_2@mail.com')

        self.set_credentials(user_2)
        response = self.client.get(f'/api/teams/{self.team.id}/progress-metrics', {
            'start': format_date(timezone.now() - timedelta(days=5)),
            'end': format_date(timezone.now() - timedelta(days=5)),
            'group': 'week'
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permissions_another_user_but_another_team_lead(self):
        another_team_lead = self.create_user('user_2@mail.com')

        TeamMemberFactory.create(team=TeamFactory.create(),
                                 user=another_team_lead,
                                 roles=TeamMember.roles.leader)

        self.set_credentials(another_team_lead)
        response = self.client.get(
            f'/api/teams/{self.team.id}/progress-metrics', {
                'start': format_date(timezone.now() - timedelta(days=5)),
                'end': format_date(timezone.now() - timedelta(days=5)),
                'group': 'week'
            })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bad_group(self):
        self.set_credentials()

        with self.assertRaises(ValueError):
            self.client.get(
                f'/api/teams/{self.team.id}/progress-metrics', {
                    'start': format_date(timezone.now() - timedelta(days=5)),
                    'end': format_date(timezone.now() - timedelta(days=5)),
                    'group': 'test'
                })

    def _create_spent_time(self, date, spent: timedelta = None, user=None,
                           issue=None):
        return IssueSpentTimeFactory.create(date=date,
                                            user=user or self.developer,
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
            self.assertEqual(metric['end'], format_date(
                parse_date(metric['start']) + timedelta(weeks=1)))

            self._check_metric(metric, 'time_spent', spents)
            self._check_metric(metric, 'time_estimate', time_estimates)

            if metric['start'] in efficiencies:
                self.assertEqual(efficiencies[metric['start']],
                                 metric['efficiency'],
                                 f'bad efficiency for {metric["start"]}: '
                                 f'expected - {efficiencies[metric["start"]]}, '
                                 f'actual - {metric["efficiency"]}')
            else:
                self.assertEqual(metric['efficiency'], 0,
                                 f'bad efficiency for {metric["start"]}: '
                                 f'expected - 0, '
                                 f'actual - {metric["efficiency"]}')

            if metric['start'] in issues_counts:
                self.assertEqual(issues_counts[metric['start']],
                                 metric['issues_count'])
            else:
                self.assertEqual(0, metric['issues_count'])

    def _prepare_metrics(self, metrics):
        return {
            format_date(d): time
            for d, time in metrics.items()
        }

    def _check_metric(self, metric, metric_name, values):
        if metric['start'] in values:
            self.assertEqual(
                values[metric['start']].total_seconds(),
                metric[metric_name],
                f'bad {metric_name} for {metric["start"]}: '
                f'expected - {values[metric["start"]]}, '
                f'actual - {timedelta(seconds=metric[metric_name])}'
            )
        else:
            self.assertEqual(
                0,
                metric[metric_name],
                f'bad {metric_name} for {metric["start"]}: '
                f'expected - 0, '
                f'actual - {timedelta(seconds=metric[metric_name])}'
            )