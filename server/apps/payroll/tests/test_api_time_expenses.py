from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.models import TeamMember
from apps.development.tests.factories import IssueFactory, TeamMemberFactory, TeamFactory
from apps.payroll.tests.factories import IssueSpentTimeFactory
from apps.users.tests.factories import UserFactory


class ApiTimeExpensesTests(BaseAPITest):
    def test_list(self):
        issue = IssueFactory.create()

        spend_1 = IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=4),
                                               user=self.user,
                                               base=issue,
                                               time_spent=int(timedelta(hours=5).total_seconds()))

        spend_2 = IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=2),
                                               user=self.user,
                                               base=issue,
                                               time_spent=int(timedelta(hours=2).total_seconds()))

        spend_3 = IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=3),
                                               user=self.user,
                                               base=issue,
                                               time_spent=int(timedelta(hours=4).total_seconds()))

        spend_4 = IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=1),
                                               user=self.user,
                                               base=issue,
                                               time_spent=int(timedelta(minutes=10).total_seconds()))

        self.set_credentials()
        response = self.client.get(f'/api/users/{self.user.id}/time-expenses')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_time_expences(response.data, [spend_1, spend_2, spend_3, spend_4])

    def test_filter_by_user(self):
        user_2 = UserFactory.create()

        issue = IssueFactory.create()

        IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=4),
                                     user=self.user,
                                     base=issue,
                                     time_spent=int(timedelta(hours=5).total_seconds()))

        spend_2 = IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=2),
                                               user=user_2,
                                               base=issue,
                                               time_spent=int(timedelta(hours=2).total_seconds()))

        IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=3),
                                     user=self.user,
                                     base=issue,
                                     time_spent=int(timedelta(hours=4).total_seconds()))

        spend_4 = IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=1),
                                               user=user_2,
                                               base=issue,
                                               time_spent=int(timedelta(minutes=10).total_seconds()))

        self.set_credentials()
        response = self.client.get(f'/api/users/{self.user.id}/time-expenses')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_time_expences(response.data, [spend_2, spend_4])

    def test_filter_by_date(self):
        issue = IssueFactory.create()

        IssueSpentTimeFactory.create(date=timezone.now() - timedelta(weeks=1, hours=1),
                                     user=self.user,
                                     base=issue,
                                     time_spent=int(timedelta(hours=5).total_seconds()))

        spend_2 = IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=2),
                                               user=self.user,
                                               base=issue,
                                               time_spent=int(timedelta(hours=2).total_seconds()))

        IssueSpentTimeFactory.create(date=timezone.now() - timedelta(days=1, hours=1),
                                     user=self.user,
                                     base=issue,
                                     time_spent=int(timedelta(hours=4).total_seconds()))

        spend_4 = IssueSpentTimeFactory.create(date=timezone.now() - timedelta(hours=1),
                                               user=self.user,
                                               base=issue,
                                               time_spent=int(timedelta(minutes=10).total_seconds()))

        self.set_credentials()
        response = self.client.get(f'/api/users/{self.user.id}/time-expenses', {
            'date': self.format_date(timezone.now())
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_time_expences(response.data, [spend_2, spend_4])

    def test_permissions_self(self):
        self.set_credentials()
        response = self.client.get(f'/api/users/{self.user.id}/time-expenses')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permissions_another_user(self):
        user_2 = self.create_user('user_2@mail.com')

        self.set_credentials()
        response = self.client.get(f'/api/users/{user_2.id}/time-expenses')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permissions_another_user_but_team_lead(self):
        user_2 = self.create_user('user_2@mail.com')

        team = TeamFactory.create()

        TeamMemberFactory.create(team=team,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team,
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        self.set_credentials()
        response = self.client.get(f'/api/users/{user_2.id}/time-expenses')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permissions_another_user_but_another_team_lead(self):
        user_2 = self.create_user('user_2@mail.com')

        TeamMemberFactory.create(team=TeamFactory.create(),
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=TeamFactory.create(),
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        self.set_credentials()
        response = self.client.get(f'/api/users/{user_2.id}/time-expenses')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permissions_another_user_but_team_developer(self):
        user_2 = self.create_user('user_2@mail.com')

        self.set_credentials()
        response = self.client.get(f'/api/users/{user_2.id}/time-expenses')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _check_time_expences(self, data, spends):
        self.assertEqual(data['count'], len(spends))

        for i, spend in enumerate(spends):
            expense = data['results'][i]

            expense['id'] = spend.id
            expense['date'] = spend.date
            expense['issue']['id'] = spend.base.id
            expense['time_spent'] = spend.time_spent
            expense['earnings'] = spend.earnings
