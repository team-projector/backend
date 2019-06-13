from rest_framework import status

from tests.base import BaseAPITest
from apps.development.models import TeamMember
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_users.factories import UserFactory


class ApiTeamMembersTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.team = TeamFactory.create()

    def test_empty_team(self):
        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/members')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['count'])

    def test_list(self):
        user_2 = UserFactory.create()
        TeamMemberFactory.create(user=self.user, team=self.team, roles=TeamMember.roles.leader)
        TeamMemberFactory.create(user=user_2, team=self.team, roles=TeamMember.roles.developer)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/members')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_list_with_roles(self):
        member_1 = TeamMemberFactory.create(user=self.user, team=self.team, roles=TeamMember.roles.leader)
        member_2 = TeamMemberFactory.create(user=UserFactory.create(), team=self.team, roles=TeamMember.roles.developer)
        member_3 = TeamMemberFactory.create(user=UserFactory.create(), team=self.team,
                                            roles=TeamMember.roles.developer | TeamMember.roles.watcher)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/members')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

        response = self.client.get(f'/api/teams/{self.team.id}/members', {'roles': 'leader'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], member_1.id)

        response = self.client.get(f'/api/teams/{self.team.id}/members', {'roles': 'developer'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIn(member_2.id, [x['id'] for x in response.data['results']])
        self.assertIn(member_3.id, [x['id'] for x in response.data['results']])

        response = self.client.get(f'/api/teams/{self.team.id}/members', {'roles': 'developer,watcher'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIn(member_2.id, [x['id'] for x in response.data['results']])
        self.assertIn(member_3.id, [x['id'] for x in response.data['results']])

        response = self.client.get(f'/api/teams/{self.team.id}/members', {'roles': 'watcher'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertIn(member_3.id, [x['id'] for x in response.data['results']])

        response = self.client.get(f'/api/teams/{self.team.id}/members', {'roles': 'watcher,test'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['roles'][0], 'Unknown choice: test')
