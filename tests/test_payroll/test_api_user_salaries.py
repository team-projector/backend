from rest_framework import status

from apps.development.models import TeamMember
from apps.payroll.services.metrics.user import User
from tests.base import BaseAPITest
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import SalaryFactory


class UserSalariesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.user = User.objects.create_user(login='user')

    def test_list(self):
        SalaryFactory.create_batch(10, user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/users/{self.user.id}/salaries')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 10)

    def test_another_user(self):
        SalaryFactory.create_batch(10, user=User.objects.create_user(login='user_2'))

        self.set_credentials()
        response = self.client.get(f'/api/users/{self.user.id}/salaries')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_bad_user(self):
        user_2 = User.objects.create_user(login='user_2')
        SalaryFactory.create_batch(10, user=user_2)

        self.set_credentials()
        response = self.client.get(f'/api/users/{user_2.id}/salaries')

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

        SalaryFactory.create_batch(10, user=user_2)

        self.set_credentials()
        response = self.client.get(f'/api/users/{user_2.id}/salaries')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 10)
