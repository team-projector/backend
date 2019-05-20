from django.utils import timezone
from rest_framework import status

from apps.development.models import TeamMember
from tests.base import BaseAPITest
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories import UserFactory


class SalariesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.team = TeamFactory.create()
        TeamMemberFactory.create(team=self.team, user=self.user, roles=TeamMember.roles.project_manager)

    @property
    def data(self):
        return {
            'charged_time': 3,
            'payed': True,
            'bonus': 10.15,
            'period_to': timezone.now().date() + timezone.timedelta(days=1),
            'taxes': 1.65,
            'penalty': 2.75,
            'period_from': timezone.now().date() - timezone.timedelta(days=1),
            'sum': 50.15,
            'total': 10.25
        }

    def test_retrieve_not_found(self):
        self.set_credentials()
        response = self.client.get('/api/salaries/1')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_another_user(self):
        user_2 = UserFactory.create()
        TeamMemberFactory.create(team=self.team, user=user_2)

        salary_1 = SalaryFactory.create(user=self.user)
        salary_2 = SalaryFactory.create(user=user_2)

        self.set_credentials()
        response = self.client.get(f'/api/salaries/{salary_1.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], salary_1.id)

        response = self.client.get(f'/api/salaries/{salary_2.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], salary_2.id)

        self.set_credentials(user_2)
        response = self.client.get(f'/api/salaries/{salary_2.id}')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You can\'t view project manager resources')

    def test_retrieve(self):
        salary = SalaryFactory.create(user=self.user, **self.data)

        self.set_credentials()
        response = self.client.get(f'/api/salaries/{salary.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], salary.id)
        self.assertEqual(response.data['charged_time'], self.data['charged_time'])
        self.assertEqual(response.data['payed'], self.data['payed'])
        self.assertEqual(response.data['bonus'], str(self.data['bonus']))
        self.assertEqual(response.data['period_to'], str(self.data['period_to']))
        self.assertEqual(response.data['taxes'], str(self.data['taxes']))
        self.assertEqual(response.data['penalty'], str(self.data['penalty']))
        self.assertEqual(response.data['period_from'], str(self.data['period_from']))
        self.assertEqual(response.data['sum'], str(self.data['sum']))
        self.assertEqual(response.data['total'], str(self.data['total']))
        self.assertIsNotNone(response.data['created_at'])
