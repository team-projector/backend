from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.development.models import Note
from apps.development.tests.factories import IssueFactory, IssueNoteFactory
from apps.users.models import User


class AdjustNotesSpentTests(TestCase):
    def setUp(self):
        self.issue = IssueFactory.create()
        self.user = User.objects.create_user(login='user', gl_id=10)

    def test_simple(self):
        self.create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=2), timedelta(hours=1))
        self.create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=1), timedelta(hours=5))
        self.create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=1), -timedelta(hours=3))
        reset = self.create_note(Note.TYPE.reset_spend, timezone.now() - timedelta(minutes=30))

        self.issue.adjust_notes_spent()

        reset.refresh_from_db()
        self.assertTrue('spent' in reset.data)
        self.assertEqual(reset.data['spent'], -timedelta(hours=3).total_seconds())

    def test_many_resets(self):
        self.create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=2), timedelta(hours=1))
        self.create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=1), timedelta(hours=5))
        self.create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=1), -timedelta(hours=3))
        reset_1 = self.create_note(Note.TYPE.reset_spend, timezone.now() - timedelta(minutes=30))

        self.create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=5), -timedelta(hours=3))
        self.create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=6), timedelta(hours=4))
        reset_2 = self.create_note(Note.TYPE.reset_spend, timezone.now() - timedelta(hours=4))

        self.issue.adjust_notes_spent()

        reset_1.refresh_from_db()
        self.assertTrue('spent' in reset_1.data)
        self.assertEqual(reset_1.data['spent'], -timedelta(hours=3).total_seconds())

        reset_2.refresh_from_db()
        self.assertTrue('spent' in reset_2.data)
        self.assertEqual(reset_2.data['spent'], -timedelta(hours=1).total_seconds())

    def test_only_reset(self):
        reset = self.create_note(Note.TYPE.reset_spend, timezone.now() - timedelta(minutes=30))

        self.issue.adjust_notes_spent()

        reset.refresh_from_db()
        self.assertTrue('spent' in reset.data)
        self.assertEqual(reset.data['spent'], 0)

    def test_multi_user_reset(self):
        user_2 = User.objects.create_user(login='user 2', gl_id=11)

        self.create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=6), timedelta(hours=4), user_2)
        self.create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=5), -timedelta(hours=3), user_2)
        reset_1 = self.create_note(Note.TYPE.reset_spend, timezone.now() - timedelta(hours=4), user=user_2)

        self.create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=4), timedelta(hours=5))
        self.create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=2), timedelta(hours=1))
        self.create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=1), timedelta(hours=5))
        self.create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=1), -timedelta(hours=3))
        reset_2 = self.create_note(Note.TYPE.reset_spend, timezone.now() - timedelta(minutes=30))

        self.create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=1), timedelta(hours=5), user_2)
        reset_3 = self.create_note(Note.TYPE.reset_spend, timezone.now() - timedelta(minutes=30), user=user_2)

        self.issue.adjust_notes_spent()

        reset_1.refresh_from_db()
        self.assertTrue('spent' in reset_1.data)
        self.assertEqual(reset_1.data['spent'], -timedelta(hours=1).total_seconds())

        reset_2.refresh_from_db()
        self.assertTrue('spent' in reset_2.data)
        self.assertEqual(reset_2.data['spent'], -timedelta(hours=8).total_seconds())

        reset_3.refresh_from_db()
        self.assertTrue('spent' in reset_3.data)
        self.assertEqual(reset_3.data['spent'], -timedelta(hours=5).total_seconds())

    def create_note(self, note_type, created_at, spent: timedelta = None, user=None):
        return IssueNoteFactory.create(type=note_type,
                                  created_at=created_at,
                                  user=user or self.user,
                                  content_object=self.issue,
                                  data={'spent': spent.total_seconds()} if spent else {})
