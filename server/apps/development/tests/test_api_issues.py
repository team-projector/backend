from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.tests.factories import IssueFactory


class ApiIssuesTests(BaseAPITest):
    def test_list(self):
        IssueFactory.create_batch(5, employee=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_search(self):
        issue = IssueFactory.create(title='create', employee=self.user)
        IssueFactory.create(title='implement', employee=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'q': 'cre'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)

    def test_filter_by_employee(self):
        user_2 = self.create_user('user_2')

        IssueFactory.create_batch(3, employee=self.user)
        issue = IssueFactory.create(employee=user_2)

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'employee': user_2.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)

    def test_filter_by_state(self):
        IssueFactory.create(employee=self.user, state='opened')
        issue = IssueFactory.create(employee=self.user, state='closed')

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'state': 'closed'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)

    def test_filter_by_due_date(self):
        now = timezone.now()
        issue = IssueFactory.create(employee=self.user, state='opened', due_date=now)
        IssueFactory.create(employee=self.user, due_date=now + timedelta(days=1))
        IssueFactory.create(employee=self.user, due_date=now - timedelta(days=1))

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'due_date': timezone.now().date().isoformat()
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)

    def test_filter_by_due_date_and_state(self):
        now = timezone.now()
        issue = IssueFactory.create(employee=self.user, state='opened', due_date=now)
        IssueFactory.create(employee=self.user, state='closed', due_date=now + timedelta(days=1))
        IssueFactory.create(employee=self.user, state='closed', due_date=now - timedelta(days=1))
        IssueFactory.create(employee=self.user, state='opened', due_date=now - timedelta(days=1))

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'due_date': timezone.now().date().isoformat(),
            'state': 'opened'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)
