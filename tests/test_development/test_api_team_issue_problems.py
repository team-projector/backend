from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from apps.development.models.issue import STATE_CLOSED
from apps.development.services.problems.issues import (
    PROBLEM_EMPTY_DUE_DAY, PROBLEM_EMPTY_ESTIMATE, PROBLEM_OVER_DUE_DAY
)
from tests.base import BaseAPITest
from tests.test_development.factories import TeamFactory, TeamMemberFactory, IssueFactory
from tests.test_users.factories import UserFactory


class ApiTeamIssuesProblemsTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.team = TeamFactory.create()
        TeamMemberFactory.create(user=self.user, team=self.team)

    def test_empty_due_day(self):
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/problems', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        issue = response.data['results'][0]
        self.assertEqual(issue['issue']['id'], problem_issue.id)
        self.assertEqual(issue['problems'], [PROBLEM_EMPTY_DUE_DAY])

    def test_empty_due_day_but_closed(self):
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        IssueFactory.create(user=self.user, state=STATE_CLOSED)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/problems', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_overdue_due_day(self):
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(user=self.user, due_date=timezone.now() - timedelta(days=1))

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/problems', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        issue = response.data['results'][0]
        self.assertEqual(issue['issue']['id'], problem_issue.id)
        self.assertEqual(issue['problems'], [PROBLEM_OVER_DUE_DAY])

    def test_overdue_due_day_but_closed(self):
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        IssueFactory.create(user=self.user,
                            due_date=timezone.now() - timedelta(days=1),
                            state=STATE_CLOSED)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/problems', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_empty_estimate(self):
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(user=self.user, due_date=timezone.now(), time_estimate=None)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/problems', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        issue = response.data['results'][0]
        self.assertEqual(issue['issue']['id'], problem_issue.id)
        self.assertEqual(issue['problems'], [PROBLEM_EMPTY_ESTIMATE])

    def test_two_errors_per_issue(self):
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(user=self.user, time_estimate=None)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/problems', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        issue = response.data['results'][0]
        self.assertEqual(issue['issue']['id'], problem_issue.id)
        self.assertEqual(set(issue['problems']), {PROBLEM_EMPTY_ESTIMATE, PROBLEM_EMPTY_DUE_DAY})

    def test_no_user_filter(self):
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(user=self.user, time_estimate=None)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/problems')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        issue = response.data['results'][0]
        self.assertEqual(issue['issue']['id'], problem_issue.id)
        self.assertEqual(set(issue['problems']), {PROBLEM_EMPTY_ESTIMATE, PROBLEM_EMPTY_DUE_DAY})

    def test_empty_due_day_but_another_user(self):
        user_2 = UserFactory.create()
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        IssueFactory.create(user=user_2)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/problems', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_empty_due_day_another_team(self):
        user_2 = UserFactory.create()
        team_2 = TeamFactory.create()
        TeamMemberFactory.create(user=user_2, team=team_2)

        issue_1 = IssueFactory.create(user=self.user)
        issue_2 = IssueFactory.create(user=user_2)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/problems')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['issue']['id'], issue_1.id)

        response = self.client.get(f'/api/teams/{team_2.id}/problems')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['issue']['id'], issue_2.id)

    def test_empty_due_day_one_team(self):
        user_2 = UserFactory.create()
        TeamMemberFactory.create(user=user_2, team=self.team)

        issue_1 = IssueFactory.create(user=self.user)
        issue_2 = IssueFactory.create(user=user_2)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/problems', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['issue']['id'], issue_1.id)

        response = self.client.get(f'/api/teams/{self.team.id}/problems', {
            'user': user_2.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['issue']['id'], issue_2.id)

        response = self.client.get(f'/api/teams/{self.team.id}/problems')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIn(issue_1.id, [x['issue']['id'] for x in response.data['results']])
        self.assertIn(issue_2.id, [x['issue']['id'] for x in response.data['results']])
