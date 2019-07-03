from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from apps.development.models import TeamMember
from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory, TeamFactory, \
    TeamMemberFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories import UserFactory


class ApiIssuesSummaryTests(BaseAPITest):
    def test_one_user(self):
        IssueFactory.create_batch(
            5, user=self.user,
            total_time_spent=0,
            due_date=timezone.now()
        )

        self.set_credentials()
        response = self.client.get('/api/issues/summary', {
            'user': self.user.id
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self._check_summary(response.data, 5, 0, 0)

    def test_filter_by_user(self):
        IssueFactory.create_batch(5, user=self.user, total_time_spent=0,
                                  due_date=timezone.now())

        another_user = UserFactory.create()
        IssueFactory.create_batch(5, user=another_user, total_time_spent=0,
                                  due_date=timezone.now())

        self.set_credentials()
        response = self.client.get('/api/issues/summary', {
            'user': self.user.id
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self._check_summary(response.data, 5, 0, 0)

    def test_time_spents_by_user(self):
        issues = IssueFactory.create_batch(5, user=self.user,
                                           due_date=timezone.now())

        another_user = UserFactory.create()

        IssueSpentTimeFactory.create(
            date=timezone.now(),
            user=another_user,
            base=IssueFactory.create(user=another_user),
            time_spent=300
        )

        IssueSpentTimeFactory.create(
            date=timezone.now(),
            user=self.user,
            base=issues[0],
            time_spent=100
        )

        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(days=2),
            user=self.user,
            base=issues[0],
            time_spent=200
        )

        self.set_credentials()
        response = self.client.get('/api/issues/summary', {
            'user': self.user.id,
            'due_date': timezone.now().date()
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self._check_summary(
            response.data,
            5,
            100,
            0
        )

    def test_time_spents_by_team(self):
        issues = IssueFactory.create_batch(5, user=self.user,
                                           due_date=timezone.now())

        another_user = UserFactory.create()

        team = TeamFactory.create()
        TeamMemberFactory.create(
            user=self.user,
            team=team,
            roles=TeamMember.roles.leader
        )

        TeamMemberFactory.create(
            user=another_user,
            team=TeamFactory.create(),
            roles=TeamMember.roles.developer
        )

        IssueSpentTimeFactory.create(
            date=timezone.now(),
            user=another_user,
            base=IssueFactory.create(user=another_user),
            time_spent=300
        )

        IssueSpentTimeFactory.create(
            date=timezone.now(),
            user=self.user,
            base=issues[0],
            time_spent=100
        )

        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(days=2),
            user=self.user,
            base=issues[0],
            time_spent=200
        )

        self.set_credentials()
        response = self.client.get('/api/issues/summary', {
            'team': team.id,
            'due_date': timezone.now().date()
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self._check_summary(
            response.data,
            5,
            100,
            0
        )

    def test_problems(self):
        IssueFactory.create_batch(
            4,
            user=self.user,
            total_time_spent=0
        )
        IssueFactory.create_batch(
            1,
            user=self.user,
            total_time_spent=0,
            due_date=timezone.now()
        )

        IssueFactory.create_batch(
            2,
            user=UserFactory.create(),
            total_time_spent=0
        )

        self.set_credentials()
        response = self.client.get('/api/issues/summary', {
            'user': self.user.id
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self._check_summary(response.data, 5, 0, 4)

    def _check_summary(self, data, issues_count, time_spent, problems_count):
        self.assertEqual(issues_count, data['issues_count'])
        self.assertEqual(time_spent, data['time_spent'])
        self.assertEqual(problems_count, data['problems_count'])
