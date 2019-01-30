from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.models import Note
from apps.development.tests.factories import IssueNoteFactory


class ApiMetricsDaysTests(BaseAPITest):
    def test_simple(self):
        self.create_note(Note.TYPE.time_spend, timezone.now() - timedelta(days=7), timedelta(hours=4))
        self.create_note(Note.TYPE.time_spend, timezone.now() - timedelta(days=5), -timedelta(hours=3))
        self.create_note(Note.TYPE.time_spend, timezone.now() + timedelta(days=5), timedelta(hours=3))

        self.set_credentials()
        response = self.client.get('/api/metrics', {
            'user': self.user.id,
            'start': self.format_date(timezone.now() - timedelta(days=10)),
            'end': self.format_date(timezone.now() + timedelta(days=10)),
            'group': 'day'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def create_note(self, note_type, created_at, spent: timedelta = None, user=None):
        return IssueNoteFactory.create(type=note_type,
                                       created_at=created_at,
                                       user=user or self.user,
                                       data={'spent': spent.total_seconds()} if spent else {})
