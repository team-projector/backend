from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.models import Note, STATE_CLOSED, STATE_OPENED
from apps.development.tests.factories import IssueFactory, IssueNoteFactory
from apps.users.models import User


class ApiIssuesTests(BaseAPITest):
    def test_list(self):
        IssueFactory.create_batch(5, user=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_list_with_metrics(self):
        IssueFactory.create_batch(5, user=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)
        self.assertTrue(all(item['metrics'] is not None for item in response.data['results']))

    def test_list_without_metrics(self):
        IssueFactory.create_batch(5, user=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues', {'metrics': 'false'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)
        self.assertTrue(all(item['metrics'] is None for item in response.data['results']))

    def test_search(self):
        issue = IssueFactory.create(title='create', user=self.user)
        IssueFactory.create(title='implement', user=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'q': 'cre'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)

    def test_filter_by_user(self):
        user_2 = self.create_user('user_2')

        IssueFactory.create_batch(3, user=self.user)
        issue = IssueFactory.create(user=user_2)

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'user': user_2.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)

    def test_filter_by_state(self):
        IssueFactory.create(user=self.user, state=STATE_OPENED)
        issue = IssueFactory.create(user=self.user, state=STATE_CLOSED)

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'state': STATE_CLOSED
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)

    def test_filter_by_due_date(self):
        now = timezone.now()
        issue = IssueFactory.create(user=self.user, state=STATE_OPENED, due_date=now)
        IssueFactory.create(user=self.user, due_date=now + timedelta(days=1))
        IssueFactory.create(user=self.user, due_date=now - timedelta(days=1))

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'due_date': self.format_date(timezone.now())
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)

    def test_filter_by_due_date_and_state(self):
        now = timezone.now()
        issue = IssueFactory.create(user=self.user, state=STATE_OPENED, due_date=now)
        IssueFactory.create(user=self.user, state=STATE_CLOSED, due_date=now + timedelta(days=1))
        IssueFactory.create(user=self.user, state=STATE_CLOSED, due_date=now - timedelta(days=1))
        IssueFactory.create(user=self.user, state=STATE_OPENED, due_date=now - timedelta(days=1))

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'due_date': self.format_date(timezone.now()),
            'state': STATE_OPENED
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)

    def test_with_spends(self):
        issue = IssueFactory.create(user=self.user,
                                    time_estimate=int(timedelta(hours=5).total_seconds()),
                                    total_time_spent=int(timedelta(hours=4).total_seconds()))

        IssueNoteFactory.create(type=Note.TYPE.time_spend,
                                created_at=timezone.now() - timedelta(hours=4),
                                user=self.user,
                                content_object=issue,
                                data={
                                    'spent': int(timedelta(hours=5).total_seconds()),
                                    'date': (timezone.now() - timedelta(hours=4)).date()
                                })

        IssueNoteFactory.create(type=Note.TYPE.time_spend,
                                created_at=timezone.now() - timedelta(hours=2),
                                user=self.user,
                                content_object=issue,
                                data={
                                    'spent': -int(timedelta(hours=1).total_seconds()),
                                    'date': (timezone.now() - timedelta(hours=2)).date()
                                })

        issue.adjust_spent_times()

        self.set_credentials()
        response = self.client.get('/api/issues', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(response.data['results'][0]['time_spent'], timedelta(hours=4).total_seconds())
        self.assertEqual(response.data['results'][0]['metrics']['remains'], timedelta(hours=1).total_seconds())

    def test_with_negative_remains(self):
        issue = IssueFactory.create(user=self.user,
                                    time_estimate=int(timedelta(hours=4).total_seconds()),
                                    total_time_spent=int(timedelta(hours=5).total_seconds()))

        IssueNoteFactory.create(type=Note.TYPE.time_spend,
                                created_at=timezone.now() - timedelta(hours=4),
                                user=self.user,
                                content_object=issue,
                                data={
                                    'spent': int(timedelta(hours=5).total_seconds()),
                                    'date': (timezone.now() - timedelta(hours=4)).date()
                                })

        issue.adjust_spent_times()

        self.set_credentials()
        response = self.client.get('/api/issues', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(response.data['results'][0]['time_spent'], timedelta(hours=5).total_seconds())
        self.assertEqual(response.data['results'][0]['metrics']['remains'], 0)

    def test_with_spends_users_mix(self):
        user_2 = User.objects.create_user(login='user 2', gl_id=11)

        issue = IssueFactory.create(user=self.user)

        IssueNoteFactory.create(type=Note.TYPE.time_spend,
                                created_at=timezone.now() - timedelta(hours=4),
                                user=self.user,
                                content_object=issue,
                                data={
                                    'spent': int(timedelta(hours=5).total_seconds()),
                                    'date': (timezone.now() - timedelta(hours=4)).date()
                                })

        IssueNoteFactory.create(type=Note.TYPE.time_spend,
                                created_at=timezone.now() - timedelta(hours=4),
                                user=self.user,
                                content_object=issue,
                                data={
                                    'spent': int(timedelta(hours=1).total_seconds()),
                                    'date': (timezone.now() - timedelta(hours=4)).date()
                                })

        IssueNoteFactory.create(type=Note.TYPE.time_spend,
                                created_at=timezone.now() - timedelta(hours=2),
                                user=user_2,
                                content_object=issue,
                                data={
                                    'spent': -int(timedelta(hours=1).total_seconds()),
                                    'date': (timezone.now() - timedelta(hours=2)).date()
                                })

        issue.adjust_spent_times()

        self.set_credentials()
        response = self.client.get('/api/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(response.data['results'][0]['time_spent'], timedelta(hours=6).total_seconds())

    def test_with_spends_reset(self):
        issue = IssueFactory.create(user=self.user)

        IssueNoteFactory.create(type=Note.TYPE.time_spend,
                                created_at=timezone.now() - timedelta(hours=4),
                                user=self.user,
                                content_object=issue,
                                data={
                                    'spent': int(timedelta(hours=5).total_seconds()),
                                    'date': (timezone.now() - timedelta(hours=4)).date()
                                })

        IssueNoteFactory.create(type=Note.TYPE.time_spend,
                                created_at=timezone.now() - timedelta(hours=4),
                                user=self.user,
                                content_object=issue,
                                data={
                                    'spent': int(timedelta(hours=1).total_seconds()),
                                    'date': (timezone.now() - timedelta(hours=4)).date()
                                })

        IssueNoteFactory.create(type=Note.TYPE.reset_spend,
                                created_at=timezone.now() - timedelta(hours=2),
                                user=self.user,
                                content_object=issue)

        IssueNoteFactory.create(type=Note.TYPE.time_spend,
                                created_at=timezone.now() - timedelta(hours=1),
                                user=self.user,
                                content_object=issue,
                                data={
                                    'spent': int(timedelta(hours=1).total_seconds()),
                                    'date': (timezone.now() - timedelta(hours=1)).date()
                                })

        issue.adjust_spent_times()

        self.set_credentials()
        response = self.client.get('/api/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(response.data['results'][0]['time_spent'], timedelta(hours=1).total_seconds())
