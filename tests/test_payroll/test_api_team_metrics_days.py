from datetime import timedelta

from django.db.models import Sum
from django.test import override_settings
from django.utils import timezone
from rest_framework import status

from apps.development.models import TeamMember
from apps.development.models.issue import STATE_OPENED
from tests.base import BaseAPITest, format_date
from tests.test_development.factories import IssueFactory, TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_payroll.mixins import CheckUserProgressMetricsMixin
from tests.test_users.factories import UserFactory


@override_settings(TP_WEEKENDS_DAYS=[])
class ApiTeamMetricsDaysTests(CheckUserProgressMetricsMixin,
                              BaseAPITest):
    def setUp(self):
        super().setUp()

        self.developer = UserFactory.create()
        self.issue = IssueFactory.create(user=self.developer, due_date=timezone.now())

        self.team = TeamFactory.create()
        TeamMemberFactory.create(team=self.team, user=self.developer, roles=TeamMember.roles.developer)
        TeamMemberFactory.create(team=self.team, user=self.user, roles=TeamMember.roles.leader)

    def test_bad_group(self):
        self.set_credentials()

        response = self.client.get(f'/api/teams/{self.team.id}/progress-metrics', {
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

        response = self.client.get(f'/api/teams/{self.team.id}/progress-metrics', {
            'start': format_date(start),
            'end': format_date(end),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)

        developer_metrics = next(item for item in response.data if item['user'] == self.developer.id)

        self.assertEqual(developer_metrics['user'], self.developer.id)
        self.assertEqual(len(developer_metrics['metrics']), (end - start).days + 1)
        self._check_metrics(developer_metrics['metrics'],
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

        response = self.client.get(f'/api/teams/{self.team.id}/progress-metrics', {
            'start': format_date(start),
            'end': format_date(end),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)

        developer_metrics = next(item for item in response.data if item['user'] == self.developer.id)

        self.assertEqual(developer_metrics['user'], self.developer.id)
        self.assertEqual(len(developer_metrics['metrics']), (end - start).days + 1)

        self._check_metrics(developer_metrics['metrics'],
                            {
                                timezone.now() - timedelta(days=4): timedelta(hours=3),
                            }, {}, {
                                timezone.now() + timedelta(days=1): 1
                            }, {
                                timezone.now() + timedelta(days=1): timedelta(hours=2)
                            }, {})

    def test_loading_day_already_has_spends(self):
        issue_2 = IssueFactory.create(user=self.developer,
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

        response = self.client.get(f'/api/teams/{self.team.id}/progress-metrics', {
            'start': format_date(start),
            'end': format_date(end),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        developer_metrics = next(item for item in response.data if item['user'] == self.developer.id)

        self.assertEqual(developer_metrics['user'], self.developer.id)
        self.assertEqual(len(developer_metrics['metrics']), (end - start).days + 1)

        self._check_metrics(developer_metrics['metrics'],
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
        response = self.client.get(f'/api/teams/{self.team.id}/progress-metrics', {
            'start': format_date(start),
            'end': format_date(end),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        developer_metrics = next(item for item in response.data if item['user'] == self.developer.id)

        self.assertEqual(developer_metrics['user'], self.developer.id)
        self.assertEqual(len(developer_metrics['metrics']), (end - start).days + 1)

        self._check_metrics(developer_metrics['metrics'],
                            {
                                timezone.now() - timedelta(days=1): timedelta(hours=1),
                                timezone.now() + timedelta(days=1): timedelta(hours=3)
                            }, {}, {
                                timezone.now(): 1
                            }, {}, {})

    def test_another_user_not_in_team(self):
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
        response = self.client.get(f'/api/teams/{self.team.id}/progress-metrics', {
            'start': format_date(start),
            'end': format_date(end),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertFalse(any(item['user'] == another_user.id for item in response.data))

    def test_another_user_in_team(self):
        another_user = UserFactory.create()
        TeamMemberFactory.create(team=self.team, user=another_user, roles=TeamMember.roles.developer)

        self._create_spent_time(timezone.now() - timedelta(days=2, hours=5), timedelta(hours=2))
        self._create_spent_time(timezone.now() - timedelta(days=1), timedelta(hours=4),
                                user=another_user)
        self._create_spent_time(timezone.now() - timedelta(days=1, hours=5), -timedelta(hours=3))
        self._create_spent_time(timezone.now() + timedelta(days=1), timedelta(hours=3), user=another_user)

        self.issue.time_estimate = timedelta(hours=4).total_seconds()
        self.issue.total_time_spent = 0
        self.issue.state = STATE_OPENED
        self.issue.save()
        self.issue.save()

        start = timezone.now() - timedelta(days=5)
        end = timezone.now() + timedelta(days=5)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/progress-metrics', {
            'start': format_date(start),
            'end': format_date(end),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        developer_metrics = next(item for item in response.data if item['user'] == self.developer.id)

        self.assertEqual(len(developer_metrics['metrics']), (end - start).days + 1)

        self._check_metrics(developer_metrics['metrics'],
                            {
                                timezone.now() - timedelta(days=2, hours=5): timedelta(hours=2),
                                timezone.now() - timedelta(days=1, hours=5): -timedelta(hours=3),
                            }, {
                                timezone.now(): timedelta(hours=4),
                            }, {
                                timezone.now(): 1,
                            }, {
                                timezone.now(): timedelta(hours=4),
                            }, {
                                timezone.now(): timedelta(hours=4),
                            })

        developer_metrics = next(item for item in response.data if item['user'] == another_user.id)

        self.assertEqual(len(developer_metrics['metrics']), (end - start).days + 1)

        self._check_metrics(developer_metrics['metrics'],
                            {
                                timezone.now() - timedelta(days=1, hours=5): timedelta(hours=4),
                                timezone.now() + timedelta(days=1): timedelta(hours=3),
                            }, {}, {}, {}, {})

    def test_permissions_leader(self):
        self.set_credentials()

        response = self.client.get(f'/api/teams/{self.team.id}/progress-metrics', {
            'start': format_date(timezone.now() - timedelta(days=5)),
            'end': format_date(timezone.now() - timedelta(days=5)),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permissions_developer(self):
        self.set_credentials(self.developer)

        response = self.client.get(f'/api/teams/{self.team.id}/progress-metrics', {
            'start': format_date(timezone.now() - timedelta(days=5)),
            'end': format_date(timezone.now() - timedelta(days=5)),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permissions_another_user(self):
        user_2 = self.create_user('user_2@mail.com')

        self.set_credentials(user_2)
        response = self.client.get(f'/api/teams/{self.team.id}/progress-metrics', {
            'start': format_date(timezone.now() - timedelta(days=5)),
            'end': format_date(timezone.now() - timedelta(days=5)),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permissions_another_user_but_another_team_lead(self):
        another_team_lead = self.create_user('user_2@mail.com')

        TeamMemberFactory.create(team=TeamFactory.create(),
                                 user=another_team_lead,
                                 roles=TeamMember.roles.leader)

        self.set_credentials(another_team_lead)
        response = self.client.get(f'/api/teams/{self.team.id}/progress-metrics', {
            'start': format_date(timezone.now() - timedelta(days=5)),
            'end': format_date(timezone.now() - timedelta(days=5)),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _create_spent_time(self, date, spent: timedelta = None, user=None, issue=None):
        return IssueSpentTimeFactory.create(date=date,
                                            user=user or self.developer,
                                            base=issue or self.issue,
                                            time_spent=spent.total_seconds())
