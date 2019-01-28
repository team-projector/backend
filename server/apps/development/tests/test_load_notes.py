from datetime import date, datetime, timedelta

from django.test import TestCase

from apps.core.utils.objects import dict2obj
from apps.development.models import Note
from apps.development.tests.factories import IssueFactory
from apps.development.utils.notes import SPEND_RESET_MESSAGE
from apps.development.utils.parsers import GITLAB_DATETIME_FORMAT, GITLAB_DATE_FORMAT
from apps.users.models import User


class LoadNotesTests(TestCase):
    def setUp(self):
        self.issue = IssueFactory.create()
        self.user = User.objects.create_user(login='user', gl_id=10)

    def test_load_spend_added(self):
        Note.objects.sync_gitlab(dict2obj({
            'id': 2,
            'body': f'added 1h 1m of time spent at {date.today():{GITLAB_DATE_FORMAT}}',
            'created_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
            'author': {
                'id': self.user.gl_id
            }
        }), self.issue)

        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.first()
        self.assertEqual(note.gl_id, 2)
        self.assertEqual(note.user, self.user)
        self.assertEqual(note.type, Note.TYPE.time_spend)
        self.assertEqual(note.data['spent'], timedelta(hours=1, minutes=1).total_seconds())

    def test_load_spend_subtracted(self):
        Note.objects.sync_gitlab(dict2obj({
            'id': 2,
            'body': f'subtracted 1h 1m of time spent at {date.today():{GITLAB_DATE_FORMAT}}',
            'created_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
            'author': {
                'id': self.user.gl_id
            }
        }), self.issue)

        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.first()
        self.assertEqual(note.gl_id, 2)
        self.assertEqual(note.user, self.user)
        self.assertEqual(note.type, Note.TYPE.time_spend)
        self.assertEqual(note.data['spent'], -timedelta(hours=1, minutes=1).total_seconds())

    def test_load_spend_reset(self):
        Note.objects.sync_gitlab(dict2obj({
            'id': 2,
            'body': SPEND_RESET_MESSAGE,
            'created_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
            'author': {
                'id': self.user.gl_id
            }
        }), self.issue)

        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.first()
        self.assertEqual(note.gl_id, 2)
        self.assertEqual(note.user, self.user)
        self.assertEqual(note.type, Note.TYPE.reset_spend)
        self.assertEqual(note.data, {})

    def test_load_unsupported(self):
        Note.objects.sync_gitlab(dict2obj({
            'id': 2,
            'body': 'bla',
            'created_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
            'author': {
                'id': self.user.gl_id
            }
        }), self.issue)

        self.assertFalse(Note.objects.exists())

    def test_load_spend_already_exists(self):
        Note.objects.create(
            gl_id=2,
            content_object=self.issue,
            user=self.user,
            data={}
        )

        self.assertEqual(Note.objects.count(), 1)

        Note.objects.sync_gitlab(dict2obj({
            'id': 2,
            'body': f'added 1h 1m of time spent at {date.today():{GITLAB_DATE_FORMAT}}',
            'created_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
            'author': {
                'id': self.user.gl_id
            }
        }), self.issue)

        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.first()
        self.assertEqual(note.gl_id, 2)
        self.assertEqual(note.user, self.user)

    def test_load_spend_already_has_another(self):
        Note.objects.create(
            gl_id=3,
            content_object=self.issue,
            user=self.user,
            data={}
        )

        self.assertEqual(Note.objects.count(), 1)

        Note.objects.sync_gitlab(dict2obj({
            'id': 2,
            'body': f'added 1h 1m of time spent at {date.today():{GITLAB_DATE_FORMAT}}',
            'created_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
            'author': {
                'id': self.user.gl_id
            }
        }), self.issue)

        self.assertEqual(Note.objects.count(), 2)
