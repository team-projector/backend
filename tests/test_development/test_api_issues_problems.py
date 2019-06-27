from contextlib import suppress
from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from apps.development.models.issue import STATE_CLOSED
from apps.development.services.problems.issues import (
    PROBLEM_EMPTY_DUE_DAY, PROBLEM_EMPTY_ESTIMATE, PROBLEM_OVER_DUE_DAY
)
from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory
from tests.test_users.factories import UserFactory


class ApiIssuesProblemsTests(BaseAPITest):
    def test_empty_due_day(self):
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        issue = self._get_issue_by_id(response.data['results'], problem_issue)
        self.assertIsNotNone(issue)
        self.assertEqual(issue['problems'], [PROBLEM_EMPTY_DUE_DAY])

    def test_empty_due_day_but_closed(self):
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        IssueFactory.create(user=self.user, state=STATE_CLOSED)

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_no_problems(response.data['results'])

    def test_overdue_due_day(self):
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(
            user=self.user,
            due_date=timezone.now() - timedelta(days=1)
        )

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        issue = self._get_issue_by_id(response.data['results'], problem_issue)
        self.assertIsNotNone(issue)
        self.assertEqual(issue['problems'], [PROBLEM_OVER_DUE_DAY])

    def test_overdue_due_day_but_closed(self):
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        IssueFactory.create(
            user=self.user,
            due_date=timezone.now() - timedelta(days=1),
            state=STATE_CLOSED
        )

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_no_problems(response.data['results'])

    def test_empty_estimate(self):
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(
            user=self.user,
            due_date=timezone.now(),
            time_estimate=None
        )

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        issue = self._get_issue_by_id(response.data['results'], problem_issue)
        self.assertIsNotNone(issue)
        self.assertEqual(issue['problems'], [PROBLEM_EMPTY_ESTIMATE])

    def test_two_errors_per_issue(self):
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(user=self.user, time_estimate=None)

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        issue = self._get_issue_by_id(response.data['results'], problem_issue)
        self.assertIsNotNone(issue)
        self.assertEqual(
            set(issue['problems']),
            {PROBLEM_EMPTY_ESTIMATE, PROBLEM_EMPTY_DUE_DAY}
        )

    def test_no_user_filter(self):
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(user=self.user, time_estimate=None)

        self.set_credentials()
        response = self.client.get('/api/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        issue = self._get_issue_by_id(response.data['results'], problem_issue)
        self.assertIsNotNone(issue)
        self.assertEqual(
            set(issue['problems']),
            {PROBLEM_EMPTY_ESTIMATE, PROBLEM_EMPTY_DUE_DAY}
        )

    def test_empty_due_day_but_another_user(self):
        user_2 = UserFactory.create()
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        IssueFactory.create(user=user_2)

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_no_problems(response.data['results'])

    def _get_issue_by_id(self, items, issue):
        with suppress(StopIteration):
            return next(item for item in items if item['id'] == issue.id)

    def _assert_no_problems(self, items):
        for item in items:
            self.assertEqual(len(item['problems']), 0)
