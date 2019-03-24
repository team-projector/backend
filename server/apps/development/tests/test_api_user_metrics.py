from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.models import TeamMember
from apps.development.tests.factories import IssueFactory, TeamFactory, TeamMemberFactory
from apps.users.tests.factories import UserFactory


class ApiUserMetrcisTests(BaseAPITest):
    def test_retrieve(self):
        IssueFactory.create_batch(10, user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/users/{self.user.id}', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertIsNotNone(response.data['metrics'])
        self.assertEqual(response.data['metrics']['issues_opened_count'], 10)

    def test_no_metrics(self):
        user = UserFactory.create()

        self.set_credentials()
        response = self.client.get(f'/api/users/{user.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertIsNone(response.data['metrics'])

    def test_another_user_but_another_team_leader(self):
        user = self.create_user('user_2@mail.com')

        TeamMemberFactory.create(team=TeamFactory.create(),
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=TeamFactory.create(),
                                 user=user,
                                 roles=TeamMember.roles.developer)

        self.set_credentials()
        response = self.client.get(f'/api/users/{user.id}', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_another_user_but_team_leader(self):
        user = self.create_user('user_2@mail.com')

        team = TeamFactory.create()

        TeamMemberFactory.create(team=team,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team,
                                 user=user,
                                 roles=TeamMember.roles.developer)

        self.set_credentials()
        response = self.client.get(f'/api/users/{user.id}', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertIsNotNone(response.data['metrics'])

    def test_another_user(self):
        user = self.create_user('user_2@mail.com')

        self.set_credentials()
        response = self.client.get(f'/api/users/{user.id}', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_me(self):
        IssueFactory.create_batch(10, user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/me/user', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertIsNotNone(response.data['metrics'])
        self.assertIsNotNone(response.data['metrics']['issues_opened_count'], 10)
