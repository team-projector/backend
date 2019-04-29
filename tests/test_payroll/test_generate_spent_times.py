from collections import defaultdict
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.development.models import Note
from apps.development.services.parsers import parse_date
from apps.payroll.models import SpentTime
from apps.users.models import User
from tests.test_development.factories import IssueFactory, IssueNoteFactory


class AdjustSpentTimesTests(TestCase):
    def setUp(self):
        self.issue = IssueFactory.create()
        self.user = User.objects.create_user(login='user', gl_id=10)

    def test_simple(self):
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=2), timedelta(hours=1))
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=1), timedelta(hours=5))
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=1), -timedelta(hours=3))
        self._create_note(Note.TYPE.reset_spend, timezone.now() - timedelta(minutes=30))

        self.issue.adjust_spent_times()

        self._check_generated_time_spents()

    def test_different_created_at_and_date(self):
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=2), timedelta(hours=1),
                          date=(timezone.now() - timedelta(days=1)).date())
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=1), timedelta(hours=5),
                          date=(timezone.now() - timedelta(days=2)).date())
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=1), -timedelta(hours=3),
                          date=(timezone.now() - timedelta(days=3)).date())
        self._create_note(Note.TYPE.reset_spend, timezone.now() - timedelta(minutes=30),
                          date=(timezone.now() - timedelta(days=5)).date())

        self.issue.adjust_spent_times()

        self._check_generated_time_spents()

    def test_many_resets(self):
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=2), timedelta(hours=1))
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=1), timedelta(hours=5))
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=1), -timedelta(hours=3))
        self._create_note(Note.TYPE.reset_spend, timezone.now() - timedelta(minutes=30))

        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=5), -timedelta(hours=3))
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=6), timedelta(hours=4))

        self.issue.adjust_spent_times()
        self._check_generated_time_spents()

    def test_only_reset(self):
        self._create_note(Note.TYPE.reset_spend, timezone.now() - timedelta(minutes=30))

        self.issue.adjust_spent_times()

        self._check_generated_time_spents()

    def test_multi_user_reset(self):
        user_2 = User.objects.create_user(login='user 2', gl_id=11)

        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=6), timedelta(hours=4), user=user_2)
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=5), -timedelta(hours=3), user=user_2)
        self._create_note(Note.TYPE.reset_spend, timezone.now() - timedelta(hours=4), user=user_2)

        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=4), timedelta(hours=5))
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=2), timedelta(hours=1))
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=1), timedelta(hours=5))
        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=1), -timedelta(hours=3))
        self._create_note(Note.TYPE.reset_spend, timezone.now() - timedelta(minutes=30))

        self._create_note(Note.TYPE.time_spend, timezone.now() - timedelta(hours=1), timedelta(hours=5), user=user_2)
        self._create_note(Note.TYPE.reset_spend, timezone.now() - timedelta(minutes=30), user=user_2)

        self.issue.adjust_spent_times()

        self._check_generated_time_spents()

    def _create_note(self, note_type, created_at, spent: timedelta = None, date=None, user=None):
        return IssueNoteFactory.create(type=note_type,
                                       created_at=created_at,
                                       updated_at=created_at,
                                       user=user or self.user,
                                       content_object=self.issue,
                                       data={
                                           'spent': spent.total_seconds(),
                                           'date': date or created_at.date()
                                       } if spent else {})

    def _check_generated_time_spents(self):
        users_spents = defaultdict(int)

        for note in self.issue.notes.all().order_by('created_at'):
            spent_time = SpentTime.objects.filter(note=note).first()

            self.assertIsNotNone(spent_time)

            if note.type == Note.TYPE.reset_spend:
                self.assertEqual(spent_time.time_spent, -users_spents[note.user_id])
                users_spents[note.user_id] = 0
            elif note.type == Note.TYPE.time_spend:
                self.assertEqual(spent_time.time_spent, note.data['spent'])
                self.assertEqual(spent_time.date, parse_date(note.data['date']))
                users_spents[note.user_id] += note.data['spent']
