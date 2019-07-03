from datetime import timedelta, date

from django.utils import timezone
from rest_framework import status

from apps.development.models import TeamMember
from tests.base import BaseAPITest
from tests.test_development.factories import (
    IssueFactory, TeamFactory, TeamMemberFactory
)
from tests.test_payroll.factories import (
    IssueSpentTimeFactory, SalaryFactory, MergeRequestSpentTimeFactory
)
from tests.test_users.factories import UserFactory


class ApiTimeExpensesTests(BaseAPITest):
    def test_list(self):
        issue = IssueFactory.create()

        spend_1 = IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=4),
            user=self.user,
            base=issue,
            time_spent=int(timedelta(hours=5).total_seconds()))

        spend_2 = IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=2),
            user=self.user,
            base=issue,
            time_spent=int(timedelta(hours=2).total_seconds()))

        spend_3 = IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=3),
            user=self.user,
            base=issue,
            time_spent=int(timedelta(hours=4).total_seconds()))

        spend_4 = IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=1),
            user=self.user,
            base=issue,
            time_spent=int(timedelta(minutes=10).total_seconds()))

        self.set_credentials()
        response = self.client.get(f'/api/time-expenses',
                                   {'user': self.user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_time_expences(response.data,
                                  [spend_1, spend_2, spend_3, spend_4])

    def test_permissions_self(self):
        self.set_credentials()
        response = self.client.get(f'/api/time-expenses',
                                   {'user': self.user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_another_user(self):
        user_2 = self.create_user('user_2@mail.com')

        self.set_credentials(user=user_2)
        response = self.client.get(f'/api/time-expenses')

        self.assertFalse(response.data['results'])

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
        response = self.client.get(f'/api/time-expenses', {'user': user_2.id})

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
        response = self.client.get(f'/api/time-expenses')

        self.assertFalse(response.data['results'])

    def test_permissions_another_user_but_team_developer(self):
        user_2 = self.create_user('user_2@mail.com')

        self.set_credentials()
        response = self.client.get(f'/api/time-expenses', {'user': user_2.id})

        self.assertFalse(response.data['results'])

    def _check_time_expences(self, data, spends):
        self.assertEqual(data['count'], len(spends))

        for i, spend in enumerate(spends):
            expense = data['results'][i]

            expense['id'] = spend.id
            expense['date'] = spend.date
            expense['owner']['id'] = spend.base.id
            expense['time_spent'] = spend.time_spent

    def test_time_expensee_filter_by_user(self):
        user_2 = UserFactory.create()
        issue = IssueFactory.create()

        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=4),
            user=self.user,
            base=issue,
            time_spent=int(timedelta(hours=5).total_seconds())
        )

        spend_2 = IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=2),
            user=user_2,
            base=issue,
            time_spent=int(timedelta(hours=2).total_seconds())
        )

        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=3),
            user=self.user,
            base=issue,
            time_spent=int(timedelta(hours=4).total_seconds())
        )

        spend_4 = IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=1),
            user=user_2,
            base=issue,
            time_spent=int(timedelta(minutes=10).total_seconds())
        )

        self._test_time_expenses_filter({'user': self.user.id},
                                        [spend_2, spend_4])

    def test_time_expenses_filter_by_team(self):
        user_2 = UserFactory.create()
        issue = IssueFactory.create()
        team_member = TeamMemberFactory.create(
            user=self.user,
            roles=TeamMember.roles.leader,
            team=TeamFactory.create()
        )

        spend_1 = IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=4),
            user=self.user,
            base=issue,
            time_spent=int(timedelta(hours=5).total_seconds())
        )

        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=2),
            user=user_2,
            base=issue,
            time_spent=int(timedelta(hours=2).total_seconds())
        )

        spend_3 = IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=3),
            user=self.user,
            base=issue,
            time_spent=int(timedelta(hours=4).total_seconds())
        )

        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=1),
            user=user_2,
            base=issue,
            time_spent=int(timedelta(minutes=10).total_seconds())
        )

        self._test_time_expenses_filter({'team': team_member.team_id},
                                        [spend_1, spend_3])

    def test_time_expenses_filter_by_salary(self):
        user_2 = UserFactory.create()
        issue = IssueFactory.create()
        salary = SalaryFactory.create(user=self.user)

        spend_1 = IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=4),
            user=self.user,
            base=issue,
            time_spent=int(timedelta(hours=5).total_seconds()),
            salary=salary
        )

        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=2),
            user=user_2,
            base=issue,
            time_spent=int(timedelta(hours=2).total_seconds())
        )

        spend_3 = IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=3),
            user=self.user,
            base=issue,
            time_spent=int(timedelta(hours=4).total_seconds()),
            salary=salary
        )

        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=1),
            user=user_2,
            base=issue,
            time_spent=int(timedelta(minutes=10).total_seconds())
        )

        self._test_time_expenses_filter({'salary': salary.id},
                                        [spend_1, spend_3])

    def test_time_expenses_filter_by_date(self):
        user_2 = UserFactory.create()
        issue = IssueFactory.create()
        spend_date = date(2019, 3, 3)

        spend_1 = IssueSpentTimeFactory.create(
            date=spend_date,
            user=self.user,
            base=issue,
            time_spent=int(timedelta(hours=5).total_seconds()),
        )

        IssueSpentTimeFactory.create(
            user=user_2,
            base=issue,
            time_spent=int(timedelta(hours=2).total_seconds()),
            date=spend_date
        )

        spend_3 = IssueSpentTimeFactory.create(
            date=spend_date,
            user=self.user,
            base=issue,
            time_spent=int(timedelta(hours=4).total_seconds()),
        )

        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=1),
            user=user_2,
            base=issue,
            time_spent=int(timedelta(minutes=10).total_seconds())
        )

        self._test_time_expenses_filter({'date': '2019-03-03'},
                                        [spend_1, spend_3])

    def test_time_expenses_filter_by_date_and_user(self):
        user_2 = UserFactory.create()
        issue = IssueFactory.create()
        spend_date = date(2019, 3, 3)

        spend_1 = IssueSpentTimeFactory.create(
            date=spend_date,
            user=self.user,
            base=issue,
            time_spent=int(timedelta(hours=5).total_seconds()),
        )

        IssueSpentTimeFactory.create(
            user=user_2,
            base=issue,
            time_spent=int(timedelta(hours=2).total_seconds()),
            date=spend_date
        )

        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=3),
            user=self.user,
            base=issue,
            time_spent=int(timedelta(hours=4).total_seconds()),
        )

        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=1),
            user=user_2,
            base=issue,
            time_spent=int(timedelta(minutes=10).total_seconds())
        )

        self._test_time_expenses_filter(
            {'date': '2019-03-03', 'user': self.user.id}, [spend_1])

    def test_time_expenses_order_by_date(self):
        issue = IssueFactory.create()

        spend_1 = IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(days=4),
            user=self.user,
            base=issue,
            time_spent=int(timedelta(hours=5).total_seconds())
        )

        spend_2 = IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(days=2),
            user=self.user,
            base=issue,
            time_spent=int(timedelta(hours=2).total_seconds())
        )

        spend_3 = IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(days=3),
            user=self.user,
            base=issue,
            time_spent=int(timedelta(hours=4).total_seconds()),
        )

        spend_4 = IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(days=1),
            user=self.user,
            base=issue,
            time_spent=int(timedelta(minutes=10).total_seconds())
        )

        self._test_time_expenses_order_by('date',
                                          [spend_1, spend_3, spend_2, spend_4])
        self._test_time_expenses_order_by('-date',
                                          [spend_4, spend_2, spend_3, spend_1])

    def test_double_spent_time(self):
        spends = IssueSpentTimeFactory.create_batch(size=10, user=self.user)

        TeamMemberFactory.create(
            team=TeamFactory.create(),
            user=self.user,
            roles=TeamMember.roles.leader | TeamMember.roles.watcher
        )
        TeamMemberFactory.create(
            team=TeamFactory.create(),
            user=self.user,
            roles=TeamMember.roles.leader | TeamMember.roles.watcher
        )

        self._test_time_expenses_filter(
            {'user': self.user.id, 'page': 1, 'page_size': 20},
            spends
        )

    def test_list_with_owner_issue(self):
        spent = IssueSpentTimeFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get('/api/time-expenses')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(
            response.data['results'][0]['owner']['id'],
            spent.base.id
        )

    def test_list_with_owner_merge_request(self):
        merge_request = MergeRequestSpentTimeFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get('/api/time-expenses')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(
            response.data['results'][0]['owner']['id'],
            merge_request.base.id
        )

    def _test_time_expenses_filter(self, user_filter, results):
        self.set_credentials()
        response = self.client.get('/api/time-expenses', user_filter)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_time_expences(response.data, results)

    def _test_time_expenses_order_by(self, param, results):
        self.set_credentials()
        response = self.client.get('/api/time-expenses', {'ordering': param})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual([x['id'] for x in response.data['results']],
                             [x.id for x in results])
