from contextlib import suppress
from datetime import timedelta

from rest_framework import status

from apps.development.models import TeamMember
from apps.users.services.problems.user import PROBLEM_PAYROLL_OPENED_OVERFLOW
from tests.base import BaseAPITest
from tests.test_development.factories import TeamMemberFactory, TeamFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories import UserFactory


class UsersProblemsApiTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.team = TeamFactory.create()

        self.user.daily_work_hours = 8
        self.user.save()

        self.another_user = UserFactory.create()
        TeamMemberFactory.create(user=self.user, team=self.team,
                                 roles=TeamMember.roles.leader)
        TeamMemberFactory.create(user=self.another_user, team=self.team,
                                 roles=TeamMember.roles.developer)

    def test_no_problems(self):
        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/members')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self._assert_no_problems(response.data['results'])

    def test_payroll_opened_overflow(self):
        self.set_credentials()

        IssueSpentTimeFactory.create(
            user=self.user,
            time_spent=timedelta(hours=5).total_seconds()
        )

        IssueSpentTimeFactory.create(
            user=self.user,
            time_spent=timedelta(hours=8).total_seconds()
        )

        response = self.client.get(f'/api/teams/{self.team.id}/members')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        user = self._get_user_by_id(response.data['results'], self.user)
        self.assertIsNotNone(user)
        self.assertEqual([PROBLEM_PAYROLL_OPENED_OVERFLOW], user['problems'])

    def test_no_payroll_opened_overflow(self):
        self.set_credentials()

        IssueSpentTimeFactory.create(
            user=self.user,
            time_spent=timedelta(hours=4).total_seconds()
        )

        IssueSpentTimeFactory.create(
            user=self.user,
            time_spent=timedelta(hours=8).total_seconds()
        )

        response = self.client.get(f'/api/teams/{self.team.id}/members')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self._assert_no_problems(response.data['results'])

    def _get_user_by_id(self, items, user):
        with suppress(StopIteration):
            return next(
                item['user'] for item in items if item['user']['id'] == user.id)

    def _assert_no_problems(self, items):
        for item in items:
            self.assertEqual(0, len(item['user']['problems']))
