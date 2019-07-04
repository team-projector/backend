from contextlib import suppress

from django.utils import timezone
from rest_framework import status

from apps.development.services.problems.issues import (
    PROBLEM_EMPTY_DUE_DAY
)
from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory


class ApiIssuesFilterProblemsTests(BaseAPITest):
    def test_no_filter(self):
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'user': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        issue = self._get_issue_by_id(response.data['results'], problem_issue)
        self.assertIsNotNone(issue)
        self.assertEqual(issue['problems'], [PROBLEM_EMPTY_DUE_DAY])

    def test_only_problems(self):
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'user': self.user.id,
            'problems': 'true'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        issue = self._get_issue_by_id(response.data['results'], problem_issue)
        self.assertIsNotNone(issue)
        self.assertEqual(issue['problems'], [PROBLEM_EMPTY_DUE_DAY])

    def test_exclude_problems(self):
        IssueFactory.create_batch(2, user=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'user': self.user.id,
            'problems': 'false'
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, response.data['count'])
        self.assertIsNone(
            self._get_issue_by_id(response.data['results'], problem_issue)
        )

    def _get_issue_by_id(self, items, issue):
        with suppress(StopIteration):
            return next(item for item in items if item['id'] == issue.id)

    def _assert_no_problems(self, items):
        for item in items:
            self.assertEqual(len(item['problems']), 0)
