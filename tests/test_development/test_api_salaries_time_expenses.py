from rest_framework import status

from apps.development.models import TeamMember
from tests.base import BaseAPITest
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import SalaryFactory, IssueSpentTimeFactory


class SalariesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.team = TeamFactory.create()
        TeamMemberFactory.create(team=self.team, user=self.user, roles=TeamMember.roles.project_manager)

    def test_list_not_found(self):
        self.set_credentials()
        response = self.client.get('/api/salaries/1/time-expenses')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list(self):
        salary_1 = SalaryFactory.create(user=self.user)
        salary_2 = SalaryFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/salaries/{salary_1.id}/time-expenses')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['count'])

        spend_1 = IssueSpentTimeFactory(user=self.user, salary=salary_1, time_spent=60)
        spend_2 = IssueSpentTimeFactory(user=self.user, salary=salary_1, time_spent=30)
        spend_3 = IssueSpentTimeFactory(user=self.user, salary=salary_2, time_spent=90)

        response = self.client.get(f'/api/salaries/{salary_1.id}/time-expenses')

        self.assertTrue(response.data['count'], 2)
        self.assertTrue(spend_1.id, [x['id'] for x in response.data['results']])
        self.assertTrue(spend_2.id, [x['id'] for x in response.data['results']])

        response = self.client.get(f'/api/salaries/{salary_2.id}/time-expenses')

        self.assertTrue(response.data['count'], 1)
        self.assertTrue(response.data['results'][0]['id'], spend_3.id)
        self.assertTrue(response.data['results'][0]['time_spent'], spend_3.time_spent)
        self.assertTrue(response.data['results'][0]['issue']['id'], spend_3.base.id)
        self.assertIsNotNone(response.data['results'][0]['created_at'])
