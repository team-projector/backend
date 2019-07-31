from datetime import timedelta, datetime

from django.test import override_settings
from django.utils import timezone
from rest_framework import status

from apps.development.models import TeamMember
from tests.base import BaseAPITest, format_date
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import IssueSpentTimeFactory


@override_settings(TP_WEEKENDS_DAYS=[])
class ApiMetricsWeeksTests(BaseAPITest):
    def test_permissions_self(self):
        self.set_credentials()
        response = self.client.get(
            f'/api/users/{self.user.id}/progress-metrics', {
                'start': format_date(timezone.now() - timedelta(days=5)),
                'end': format_date(timezone.now() - timedelta(days=5)),
                'group': 'week'
            })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permissions_another_user(self):
        user_2 = self.create_user('user_2@mail.com')

        self.set_credentials()
        response = self.client.get(f'/api/users/{user_2.id}/progress-metrics', {
            'start': format_date(timezone.now() - timedelta(days=5)),
            'end': format_date(timezone.now() - timedelta(days=5)),
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
            'start': format_date(timezone.now() - timedelta(days=5)),
            'end': format_date(timezone.now() - timedelta(days=5)),
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
            'start': format_date(timezone.now() - timedelta(days=5)),
            'end': format_date(timezone.now() - timedelta(days=5)),
            'group': 'week'
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permissions_another_user_but_team_developer(self):
        user_2 = self.create_user('user_2@mail.com')

        self.set_credentials()
        response = self.client.get(f'/api/users/{user_2.id}/progress-metrics', {
            'start': format_date(timezone.now() - timedelta(days=5)),
            'end': format_date(timezone.now() - timedelta(days=5)),
            'group': 'week'
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bad_group(self):
        self.set_credentials()

        self.client.get(f'/api/users/{self.user.id}/progress-metrics', {
            'start': datetime.now() - timedelta(days=5),
            'end': datetime.now() + timedelta(days=5),
            'group': 'test'
        })

    def _create_spent_time(self, date, spent: timedelta = None, user=None,
                           issue=None):
        return IssueSpentTimeFactory.create(date=date,
                                            user=user or self.user,
                                            base=issue or self.issue,
                                            time_spent=spent.total_seconds())
