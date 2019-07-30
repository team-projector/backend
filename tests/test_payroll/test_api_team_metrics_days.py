from datetime import timedelta, datetime
from django.test import override_settings
from django.utils import timezone
from rest_framework import status

from apps.development.models import TeamMember
from tests.base import BaseAPITest, format_date
from tests.test_development.factories import IssueFactory, TeamFactory, \
    TeamMemberFactory
from tests.test_users.factories import UserFactory


@override_settings(TP_WEEKENDS_DAYS=[])
class ApiTeamMetricsDaysTests(BaseAPITest):
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

    def test_permissions_leader(self):
        self.set_credentials()

        response = self.client.get(
            f'/api/teams/{self.team.id}/progress-metrics', {
                'start': format_date(timezone.now() - timedelta(days=5)),
                'end': format_date(timezone.now() - timedelta(days=5)),
                'group': 'day'
            })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permissions_developer(self):
        self.set_credentials(self.developer)

        response = self.client.get(
            f'/api/teams/{self.team.id}/progress-metrics', {
                'start': format_date(timezone.now() - timedelta(days=5)),
                'end': format_date(timezone.now() - timedelta(days=5)),
                'group': 'day'
            })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permissions_another_user(self):
        user_2 = self.create_user('user_2@mail.com')

        self.set_credentials(user_2)
        response = self.client.get(
            f'/api/teams/{self.team.id}/progress-metrics', {
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
        response = self.client.get(
            f'/api/teams/{self.team.id}/progress-metrics', {
                'start': format_date(timezone.now() - timedelta(days=5)),
                'end': format_date(timezone.now() - timedelta(days=5)),
                'group': 'day'
            })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
