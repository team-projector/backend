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
        TeamMemberFactory.create(team=self.team, user=self.user)

        self.set_credentials()
        response = self.client.get('/api/salaries/1')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve(self):
        TeamMemberFactory.create(team=self.team, user=self.user)
        salary = SalaryFactory.create(user=self.user, **self.data)

        self.set_credentials()
        response = self.client.get(f'/api/salaries/{salary.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], salary.id)
        self.assertEqual(response.data['charged_time'], self.data['charged_time'])
        self.assertEqual(response.data['payed'], self.data['payed'])
        self.assertEqual(float(response.data['bonus']), self.data['bonus'])
        self.assertEqual(response.data['period_to'], str(self.data['period_to']))
        self.assertEqual(float(response.data['taxes']), self.data['taxes'])
        self.assertEqual(float(response.data['penalty']), self.data['penalty'])
        self.assertEqual(response.data['period_from'], str(self.data['period_from']))
        self.assertEqual(float(response.data['sum']), self.data['sum'])
        self.assertEqual(float(response.data['total']), self.data['total'])
        self.assertIsNotNone(response.data['created_at'])

    def test_permissions(self):
        developer = UserFactory.create()
        TeamMemberFactory.create(team=self.team, user=developer)
        salary_developer = SalaryFactory.create(user=developer)

        developer_another_team = UserFactory.create()
        TeamMemberFactory.create(team=TeamFactory.create(), user=developer_another_team)
        salary_developer_another = SalaryFactory.create(user=developer_another_team)

        team_leader = UserFactory.create()
        TeamMemberFactory.create(team=self.team, user=team_leader, roles=TeamMember.roles.leader)
        salary_team_leader = SalaryFactory.create(user=team_leader)

        self.set_credentials(developer)
        response = self.client.get(f'/api/salaries/{salary_developer.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], salary_developer.id)

        response = self.client.get(f'/api/salaries/{salary_team_leader.id}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You can\'t view user salaries')

        response = self.client.get(f'/api/salaries/{salary_developer_another.id}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.set_credentials(team_leader)
        response = self.client.get(f'/api/salaries/{salary_developer.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], salary_developer.id)

        response = self.client.get(f'/api/salaries/{salary_team_leader.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], salary_team_leader.id)

        response = self.client.get(f'/api/salaries/{salary_developer_another.id}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
