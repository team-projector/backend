from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.models import TeamMember
from apps.development.tests.factories import TeamFactory, TeamMemberFactory
from apps.users.tests.factories import UserFactory


class ApiTeamsTests(BaseAPITest):
    def test_list(self):
        TeamFactory.create_batch(5)

        self.set_credentials()
        response = self.client.get('/api/teams')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_filter_member(self):
        TeamFactory.create_batch(5)
        team = TeamFactory.create()

        TeamMemberFactory.create(user=self.user, team=team, roles=TeamMember.roles.leader)

        self.set_credentials()
        response = self.client.get('/api/teams', {
            'user': self.user.id,
            'roles': [TeamMember.ROLES.leader]
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], team.id)

    def test_filter_not_member(self):
        TeamFactory.create_batch(5)
        TeamFactory.create()

        self.set_credentials()
        response = self.client.get('/api/teams', {
            'user': self.user.id,
            'roles': [TeamMember.ROLES.leader]
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_filter_another_member(self):
        TeamFactory.create_batch(5)
        team = TeamFactory.create()

        user_2 = UserFactory.create()

        TeamMemberFactory.create(user=user_2, team=team, roles=TeamMember.roles.leader)

        self.set_credentials()
        response = self.client.get('/api/teams', {
            'user': self.user.id,
            'roles': [TeamMember.ROLES.leader]
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_filter_member_bad_role(self):
        TeamFactory.create_batch(5)
        team = TeamFactory.create()

        TeamMemberFactory.create(user=self.user, team=team, roles=TeamMember.roles.leader)

        self.set_credentials()
        response = self.client.get('/api/teams', {
            'user': self.user.id,
            'roles': [TeamMember.ROLES.developer]
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_filter_many_roles(self):
        TeamFactory.create_batch(5)
        team = TeamFactory.create()

        TeamMemberFactory.create(user=self.user,
                                 team=team,
                                 roles=TeamMember.roles.leader | TeamMember.roles.developer)

        self.set_credentials()
        response = self.client.get('/api/teams', {
            'user': self.user.id,
            'roles': [TeamMember.ROLES.leader]
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], team.id)

    def test_filter_querystring(self):
        TeamFactory.create_batch(5)
        team = TeamFactory.create()

        TeamMemberFactory.create(user=self.user,
                                 team=team,
                                 roles=TeamMember.roles.leader | TeamMember.roles.developer)

        self.set_credentials()
        response = self.client.get(f'/api/teams?user={self.user.id}&roles=leader&roles=developer')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], team.id)
