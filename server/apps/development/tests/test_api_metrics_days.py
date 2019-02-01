from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.models import Note
from apps.development.tests.factories import IssueFactory, IssueNoteFactory
from apps.users.tests.factories import UserFactory


class ApiMetricsDaysTests(BaseAPITest):
    def test_simple(self):
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(days=2, hours=5), timedelta(hours=2))
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(days=1), timedelta(hours=4))
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(days=1, hours=5), -timedelta(hours=3))
        self._create_note(Note.TYPE.time_spend, timezone.now() + timedelta(days=1), timedelta(hours=3))

        IssueFactory.create()

        self.set_credentials()
        response = self.client.get('/api/metrics', {
            'user': self.user.id,
            'start': self.format_date(timezone.now() - timedelta(days=5)),
            'end': self.format_date(timezone.now() + timedelta(days=5)),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        self._check_metric(response.data[0], timezone.now() - timedelta(days=2), timedelta(hours=2))
        self._check_metric(response.data[1], timezone.now() - timedelta(days=1), timedelta(hours=1))
        self._check_metric(response.data[2], timezone.now() + timedelta(days=1), timedelta(hours=3))

    def test_not_in_range(self):
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(days=5, hours=5), timedelta(hours=2))
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(days=1), timedelta(hours=4))
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(days=1, hours=5), -timedelta(hours=3))
        self._create_note(Note.TYPE.time_spend, timezone.now() + timedelta(days=1), timedelta(hours=3))

        IssueFactory.create()

        self.set_credentials()
        response = self.client.get('/api/metrics', {
            'user': self.user.id,
            'start': self.format_date(timezone.now() - timedelta(days=3)),
            'end': self.format_date(timezone.now() + timedelta(days=3)),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        self._check_metric(response.data[0], timezone.now() - timedelta(days=1), timedelta(hours=1))
        self._check_metric(response.data[1], timezone.now() + timedelta(days=1), timedelta(hours=3))

    def test_another_user(self):
        another_user = UserFactory.create()

        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(days=2, hours=5), timedelta(hours=2))
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(days=1), timedelta(hours=4),
                          user=another_user)
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(days=1, hours=5), -timedelta(hours=3))
        self._create_note(Note.TYPE.time_spend, timezone.now() + timedelta(days=1), timedelta(hours=3),
                          user=another_user)

        IssueFactory.create()

        self.set_credentials()
        response = self.client.get('/api/metrics', {
            'user': self.user.id,
            'start': self.format_date(timezone.now() - timedelta(days=5)),
            'end': self.format_date(timezone.now() + timedelta(days=5)),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        self._check_metric(response.data[0], timezone.now() - timedelta(days=2), timedelta(hours=2))
        self._check_metric(response.data[1], timezone.now() - timedelta(days=1), -timedelta(hours=3))

    def _create_note(self, note_type, created_at, spent: timedelta = None, user=None):
        return IssueNoteFactory.create(type=note_type,
                                       created_at=created_at,
                                       user=user or self.user,
                                       data={'spent': int(spent.total_seconds())} if spent else {})

    def _check_metric(self, metric, day: datetime, spent: timedelta):
        self.assertEqual(metric['start'], metric['end'])
        self.assertEqual(metric['end'], self.format_date(day))
        self.assertEqual(metric['time_spent'], spent.total_seconds())
