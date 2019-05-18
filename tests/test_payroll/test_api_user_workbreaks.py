from rest_framework import status

from apps.development.models import TeamMember
from tests.base import BaseAPITest
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories import UserFactory


class UserWorkBreaksTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()

    def test_list(self):
        WorkBreakFactory.create_batch(10, user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/users/{self.user.id}/work-breaks')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 10)

    def test_another_user(self):
        user_2 = UserFactory.create()
        WorkBreakFactory.create_batch(10, user=user_2)

        self.set_credentials()
        response = self.client.get(f'/api/users/{self.user.id}/work-breaks')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_bad_user(self):
        user_2 = UserFactory.create()
        WorkBreakFactory.create_batch(10, user=user_2)

        self.set_credentials()
        response = self.client.get(f'/api/users/{user_2.id}/work-breaks')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bad_user_but_teamlead(self):
        user_2 = self.create_user('user_2@mail.com')

        team = TeamFactory.create()

        TeamMemberFactory.create(team=team,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team,
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        WorkBreakFactory.create_batch(10, user=user_2)

        self.set_credentials()
        response = self.client.get(f'/api/users/{user_2.id}/work-breaks')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 10)
