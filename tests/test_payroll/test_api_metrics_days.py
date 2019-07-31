from datetime import timedelta, datetime
from django.test import override_settings
from rest_framework import status

from apps.development.models import TeamMember
from tests.base import BaseAPITest, format_date
from tests.test_development.factories import TeamFactory, TeamMemberFactory


@override_settings(TP_WEEKENDS_DAYS=[])
class ApiMetricsDaysTests(BaseAPITest):
    def test_permissions_self(self):
        self.set_credentials()
        response = self.client.get(f'/api/users/{self.user.id}/progress-metrics', {
            'start': format_date(datetime.now() - timedelta(days=5)),
            'end': format_date(datetime.now() - timedelta(days=5)),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permissions_another_user(self):
        user_2 = self.create_user('user_2@mail.com')

        self.set_credentials()
        response = self.client.get(f'/api/users/{user_2.id}/progress-metrics', {
            'start': format_date(datetime.now() - timedelta(days=5)),
            'end': format_date(datetime.now() - timedelta(days=5)),
            'group': 'day'
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
            'start': format_date(datetime.now() - timedelta(days=5)),
            'end': format_date(datetime.now() - timedelta(days=5)),
            'group': 'day'
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
            'start': format_date(datetime.now() - timedelta(days=5)),
            'end': format_date(datetime.now() - timedelta(days=5)),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permissions_another_user_but_team_developer(self):
        user_2 = self.create_user('user_2@mail.com')

        self.set_credentials()
        response = self.client.get(f'/api/users/{user_2.id}/progress-metrics', {
            'start': format_date(datetime.now() - timedelta(days=5)),
            'end': format_date(datetime.now() - timedelta(days=5)),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
