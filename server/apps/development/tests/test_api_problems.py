from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.tests.factories import IssueFactory
from apps.development.utils.problems.issues import (PROBLEM_EMPTY_DUE_DAY, PROBLEM_EMPTY_ESTIMATE,
                                                    PROBLEM_OVERDUE_DUE_DAY)
from apps.users.tests.factories import UserFactory


class ApiIssuesTests(BaseAPITest):
    def test_empty_due_day(self):
        IssueFactory.create_batch(2, employee=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(employee=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues/problems', {
            'employee': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        issue = response.data['results'][0]
        self.assertEqual(issue['issue']['id'], problem_issue.id)
        self.assertEqual(issue['problems'], [PROBLEM_EMPTY_DUE_DAY])

    def test_overdue_due_day(self):
        IssueFactory.create_batch(2, employee=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(employee=self.user, due_date=timezone.now() - timedelta(days=1))

        self.set_credentials()
        response = self.client.get('/api/issues/problems', {
            'employee': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        issue = response.data['results'][0]
        self.assertEqual(issue['issue']['id'], problem_issue.id)
        self.assertEqual(issue['problems'], [PROBLEM_OVERDUE_DUE_DAY])

    def test_empty_estimate(self):
        IssueFactory.create_batch(2, employee=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(employee=self.user, due_date=timezone.now(), time_estimate=None)

        self.set_credentials()
        response = self.client.get('/api/issues/problems', {
            'employee': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        issue = response.data['results'][0]
        self.assertEqual(issue['issue']['id'], problem_issue.id)
        self.assertEqual(issue['problems'], [PROBLEM_EMPTY_ESTIMATE])

    def test_two_errors_per_issue(self):
        IssueFactory.create_batch(2, employee=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(employee=self.user, time_estimate=None)

        self.set_credentials()
        response = self.client.get('/api/issues/problems', {
            'employee': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        issue = response.data['results'][0]
        self.assertEqual(issue['issue']['id'], problem_issue.id)
        self.assertEqual(set(issue['problems']), {PROBLEM_EMPTY_ESTIMATE, PROBLEM_EMPTY_DUE_DAY})

    def test_no_employee_filter(self):
        IssueFactory.create_batch(2, employee=self.user, due_date=timezone.now())
        problem_issue = IssueFactory.create(employee=self.user, time_estimate=None)

        self.set_credentials()
        response = self.client.get('/api/issues/problems')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        issue = response.data['results'][0]
        self.assertEqual(issue['issue']['id'], problem_issue.id)
        self.assertEqual(set(issue['problems']), {PROBLEM_EMPTY_ESTIMATE, PROBLEM_EMPTY_DUE_DAY})

    def test_empty_due_day_but_another_user(self):
        user_2 = UserFactory.create()
        IssueFactory.create_batch(2, employee=self.user, due_date=timezone.now())
        IssueFactory.create(employee=user_2)

        self.set_credentials()
        response = self.client.get('/api/issues/problems', {
            'employee': self.user.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
