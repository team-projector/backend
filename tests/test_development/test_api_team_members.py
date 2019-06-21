from rest_framework import status

from apps.development.models import TeamMember
from tests.base import BaseAPITest
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

    def test_list_single_with_role(self):
        leader = TeamMemberFactory.create(
            user=self.user,
            team=self.team,
            roles=TeamMember.roles.leader
        )
        TeamMemberFactory.create(
            user=UserFactory.create(),
            team=self.team,
            roles=TeamMember.roles.developer
        )
        TeamMemberFactory.create(
            user=UserFactory.create(),
            team=self.team,
            roles=TeamMember.roles.developer | TeamMember.roles.watcher
        )

        self.set_credentials()

        response = self.client.get(f'/api/teams/{self.team.id}/members', {
            'roles': 'leader'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], leader.id)

    def test_list_two_with_role(self):
        TeamMemberFactory.create(
            user=self.user,
            team=self.team,
            roles=TeamMember.roles.leader
        )
        developer_1 = TeamMemberFactory.create(
            user=UserFactory.create(),
            team=self.team,
            roles=TeamMember.roles.developer
        )
        developer_2 = TeamMemberFactory.create(
            user=UserFactory.create(),
            team=self.team,
            roles=TeamMember.roles.developer | TeamMember.roles.watcher
        )

        self.set_credentials()

        response = self.client.get(f'/api/teams/{self.team.id}/members', {
            'roles': 'developer'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIn(developer_1.id, [x['id'] for x in response.data['results']])
        self.assertIn(developer_2.id, [x['id'] for x in response.data['results']])

    def test_many_roles(self):
        user_1 = TeamMemberFactory.create(
            user=self.user,
            team=self.team,
            roles=TeamMember.roles.leader
        )
        TeamMemberFactory.create(
            user=UserFactory.create(),
            team=self.team,
            roles=TeamMember.roles.developer
        )
        user_2 = TeamMemberFactory.create(
            user=UserFactory.create(),
            team=self.team,
            roles=TeamMember.roles.leader | TeamMember.roles.developer
        )

        self.set_credentials()

        response = self.client.get(f'/api/teams/{self.team.id}/members?roles=leader&roles=watcher')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIn(user_1.id, [x['id'] for x in response.data['results']])
        self.assertIn(user_2.id, [x['id'] for x in response.data['results']])

    def test_member_has_many_roles(self):
        TeamMemberFactory.create(
            user=self.user,
            team=self.team,
            roles=TeamMember.roles.leader
        )
        TeamMemberFactory.create(
            user=UserFactory.create(),
            team=self.team,
            roles=TeamMember.roles.developer
        )
        developer = TeamMemberFactory.create(
            user=UserFactory.create(),
            team=self.team,
            roles=TeamMember.roles.developer | TeamMember.roles.watcher
        )

        self.set_credentials()

        response = self.client.get(f'/api/teams/{self.team.id}/members', {'roles': 'watcher'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertIn(developer.id, [x['id'] for x in response.data['results']])

    def test_bad_role(self):
        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/members', {'roles': ['watcher', 'test']})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
