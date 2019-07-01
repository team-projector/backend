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
        self.assertEqual(response.data['charged_time'],
                         self.data['charged_time'])
        self.assertEqual(response.data['payed'], self.data['payed'])
        self.assertEqual(float(response.data['bonus']), self.data['bonus'])
        self.assertEqual(response.data['period_to'],
                         str(self.data['period_to']))
        self.assertEqual(float(response.data['taxes']), self.data['taxes'])
        self.assertEqual(float(response.data['penalty']), self.data['penalty'])
        self.assertEqual(response.data['period_from'],
                         str(self.data['period_from']))
        self.assertEqual(float(response.data['sum']), self.data['sum'])
        self.assertEqual(float(response.data['total']), self.data['total'])
        self.assertIsNotNone(response.data['created_at'])

    def test_list(self):
        salaries = SalaryFactory.create_batch(size=5, user=self.user)

        self._test_salaries_filter({}, salaries)

    def test_list_another_user(self):
        user_2 = self.create_user('user_2@mail.com')
        SalaryFactory.create_batch(size=5, user=user_2)

        self._test_salaries_filter({'user': user_2.id}, [])

    def test_salaries_filter_by_user(self):
        user_2 = UserFactory.create()
        salaries = SalaryFactory.create_batch(size=5, user=user_2)

        team = TeamFactory.create()
        team.members.set([self.user, user_2])

        TeamMember.objects.filter(user=self.user).update(
            roles=TeamMember.roles.leader
        )

        self._test_salaries_filter({'user': user_2.id}, salaries)

    def test_salaries_filter_by_team(self):
        user_2 = UserFactory.create()
        user_3 = UserFactory.create()
        salaries = SalaryFactory.create_batch(size=5, user=user_2)
        SalaryFactory.create_batch(size=5, user=user_3)
        team = TeamFactory.create()
        team.members.set([self.user, user_2])

        TeamMember.objects.filter(user=self.user, team=team).update(
            roles=TeamMember.roles.leader)

        self._test_salaries_filter({'team': team.id}, salaries)

    def test_double_salaries(self):
        salaries = SalaryFactory.create_batch(size=10, user=self.user)

        TeamMemberFactory.create(
            team=TeamFactory.create(),
            user=self.user,
            roles=TeamMember.roles.leader
        )
        TeamMemberFactory.create(
            team=TeamFactory.create(),
            user=self.user,
            roles=TeamMember.roles.leader
        )

        self._test_salaries_filter(
            {'user': self.user.id},
            salaries
        )

    def _test_salaries_filter(self, user_filter, results):
        self.set_credentials()
        response = self.client.get('/api/salaries', user_filter)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {x['id'] for x in response.data['results']},
            {x.id for x in results}
        )
