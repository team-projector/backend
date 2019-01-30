from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.models import Note
from apps.development.tests.factories import IssueFactory, IssueNoteFactory
from apps.users.models import User


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

    def test_with_spends(self):
        issue = IssueFactory.create(employee=self.user)

        IssueNoteFactory.create(type=Note.TYPE.time_spend,
                                created_at=timezone.now() - timedelta(hours=4),
                                user=self.user,
                                content_object=issue,
                                data={'spent': int(timedelta(hours=5).total_seconds())})

        IssueNoteFactory.create(type=Note.TYPE.time_spend,
                                created_at=timezone.now() - timedelta(hours=2),
                                user=self.user,
                                content_object=issue,
                                data={'spent': -int(timedelta(hours=1).total_seconds())})

        issue.adjust_notes_spent()

        self.set_credentials()
        response = self.client.get('/api/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(response.data['results'][0]['time_spent'], timedelta(hours=4).total_seconds())

    def test_with_spends_users_mix(self):
        user_2 = User.objects.create_user(login='user 2', gl_id=11)

        issue = IssueFactory.create(employee=self.user)

        IssueNoteFactory.create(type=Note.TYPE.time_spend,
                                created_at=timezone.now() - timedelta(hours=4),
                                user=self.user,
                                content_object=issue,
                                data={'spent': int(timedelta(hours=5).total_seconds())})

        IssueNoteFactory.create(type=Note.TYPE.time_spend,
                                created_at=timezone.now() - timedelta(hours=4),
                                user=self.user,
                                content_object=issue,
                                data={'spent': int(timedelta(hours=1).total_seconds())})

        IssueNoteFactory.create(type=Note.TYPE.time_spend,
                                created_at=timezone.now() - timedelta(hours=2),
                                user=user_2,
                                content_object=issue,
                                data={'spent': -int(timedelta(hours=1).total_seconds())})

        issue.adjust_notes_spent()

        self.set_credentials()
        response = self.client.get('/api/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(response.data['results'][0]['time_spent'], timedelta(hours=6).total_seconds())

    def test_with_spends_reset(self):
        issue = IssueFactory.create(employee=self.user)

        IssueNoteFactory.create(type=Note.TYPE.time_spend,
                                created_at=timezone.now() - timedelta(hours=4),
                                user=self.user,
                                content_object=issue,
                                data={'spent': int(timedelta(hours=5).total_seconds())})

        IssueNoteFactory.create(type=Note.TYPE.time_spend,
                                created_at=timezone.now() - timedelta(hours=4),
                                user=self.user,
                                content_object=issue,
                                data={'spent': int(timedelta(hours=1).total_seconds())})

        IssueNoteFactory.create(type=Note.TYPE.reset_spend,
                                created_at=timezone.now() - timedelta(hours=2),
                                user=self.user,
                                content_object=issue)

        IssueNoteFactory.create(type=Note.TYPE.time_spend,
                                created_at=timezone.now() - timedelta(hours=1),
                                user=self.user,
                                content_object=issue,
                                data={'spent': int(timedelta(hours=1).total_seconds())})

        issue.adjust_notes_spent()

        self.set_credentials()
        response = self.client.get('/api/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(response.data['results'][0]['time_spent'], timedelta(hours=1).total_seconds())
