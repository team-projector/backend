from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.models import TeamMember
from apps.development.tests.factories import TeamFactory, TeamMemberFactory
from apps.users.tests.factories import UserFactory


class ApiTeamMembersTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.team = TeamFactory.create()

    def test_list(self):
        user_2 = UserFactory.create()
        TeamMemberFactory.create(user=self.user, team=self.team, roles=TeamMember.roles.leader)
        TeamMemberFactory.create(user=user_2, team=self.team, roles=TeamMember.roles.developer)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/members')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_none(self):
        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/members')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
