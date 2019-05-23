from rest_framework import status

from apps.development.models import TeamMember
from tests.base import BaseAPITest
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import SalaryFactory, IssueSpentTimeFactory
from tests.test_users.factories import UserFactory


class SalariesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.team = TeamFactory.create()

    def test_list_not_found(self):
        TeamMemberFactory.create(team=self.team, user=self.user)

        self.set_credentials()
        response = self.client.get('/api/salaries/1/time-expenses')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list(self):
        TeamMemberFactory.create(team=self.team, user=self.user)
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

    def test_permissions(self):
        developer = UserFactory.create()
        TeamMemberFactory.create(team=self.team, user=developer)
        salary_developer = SalaryFactory.create(user=developer)
        spend_developer = IssueSpentTimeFactory(user=self.user, salary=salary_developer, time_spent=60)

        developer_another_team = UserFactory.create()
        TeamMemberFactory.create(team=TeamFactory.create(), user=developer_another_team)
        salary_developer_another = SalaryFactory.create(user=developer_another_team)
        IssueSpentTimeFactory(user=self.user, salary=salary_developer_another, time_spent=30)

        team_leader = UserFactory.create()
        TeamMemberFactory.create(team=self.team, user=team_leader, roles=TeamMember.roles.leader)
        salary_team_leader = SalaryFactory.create(user=team_leader)
        spend_team_leader = IssueSpentTimeFactory(user=self.user, salary=salary_team_leader, time_spent=90)

        self.set_credentials(developer)
        response = self.client.get(f'/api/salaries/{salary_developer.id}/time-expenses')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], spend_developer.id)

        response = self.client.get(f'/api/salaries/{salary_team_leader.id}/time-expenses')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You can\'t view user salaries')

        response = self.client.get(f'/api/salaries/{salary_developer_another.id}/time-expenses')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.set_credentials(team_leader)
        response = self.client.get(f'/api/salaries/{salary_developer.id}/time-expenses')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], spend_developer.id)

        response = self.client.get(f'/api/salaries/{salary_team_leader.id}/time-expenses')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], spend_team_leader.id)

        response = self.client.get(f'/api/salaries/{salary_developer_another.id}/time-expenses')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
