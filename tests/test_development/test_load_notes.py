from datetime import date, datetime, timedelta

from django.test import TestCase
from django.utils import timezone

from apps.core.utils.objects import dict2obj
from apps.development.models import Note
from apps.development.services.gitlab.notes import SPEND_RESET_MESSAGE
from apps.development.services.parsers import GITLAB_DATETIME_FORMAT, GITLAB_DATE_FORMAT
from apps.users.models import User
from tests.test_development.factories import IssueFactory


class LoadNotesTests(TestCase):
    def setUp(self):
        self.issue = IssueFactory.create()
        self.user = User.objects.create_user(login='user', gl_id=10)

    def test_load_spend_added(self):
        note_date = date.today()

        body = f'added 1h 1m of time spent at {note_date:{GITLAB_DATE_FORMAT}}'

        Note.objects.sync_gitlab(dict2obj({
            'id': 2,
            'body': body,
            'created_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
            'updated_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
            'author': {
                'id': self.user.gl_id
            }
        }), self.issue)

        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.first()
        self.assertEqual(note.gl_id, 2)
        self.assertEqual(note.user, self.user)
        self.assertEqual(note.type, Note.TYPE.time_spend)
        self.assertEqual(note.body, body)
        self.assertEqual(note.data['spent'], seconds(hours=1, minutes=1))
        self.assertEqual(note.data['date'], note_date.strftime(GITLAB_DATE_FORMAT))

    def test_load_spend_subtracted(self):
        note_date = date.today()

        body = f'subtracted 1h 1m of time spent at {note_date:{GITLAB_DATE_FORMAT}}'
        Note.objects.sync_gitlab(dict2obj({
            'id': 2,
            'body': body,
            'created_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
            'updated_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
            'author': {
                'id': self.user.gl_id
            }
        }), self.issue)

        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.first()
        self.assertEqual(note.gl_id, 2)
        self.assertEqual(note.user, self.user)
        self.assertEqual(note.body, body)
        self.assertEqual(note.type, Note.TYPE.time_spend)
        self.assertEqual(note.data['spent'], -seconds(hours=1, minutes=1))
        self.assertEqual(note.data['date'], note_date.strftime(GITLAB_DATE_FORMAT))

    def test_load_spend_reset(self):
        Note.objects.sync_gitlab(dict2obj({
            'id': 2,
            'body': SPEND_RESET_MESSAGE,
            'created_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
            'updated_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
            'author': {
                'id': self.user.gl_id
            }
        }), self.issue)

        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.first()
        self.assertEqual(note.gl_id, 2)
        self.assertEqual(note.user, self.user)
        self.assertEqual(note.body, SPEND_RESET_MESSAGE)
        self.assertEqual(note.type, Note.TYPE.reset_spend)
        self.assertEqual(note.data, {})

    def test_load_unsupported(self):
        Note.objects.sync_gitlab(dict2obj({
            'id': 2,
            'body': 'bla',
            'created_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
            'updated_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
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
            'updated_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
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
            'updated_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
            'author': {
                'id': self.user.gl_id
            }
        }), self.issue)

        self.assertEqual(Note.objects.count(), 2)

    def test_load_spend_has_prior(self):
        Note.objects.create(
            gl_id=3,
            content_object=self.issue,
            user=self.user,
            created_at=timezone.now() - timedelta(hours=1),
            data={}
        )

        self.assertEqual(Note.objects.count(), 1)

        Note.objects.sync_gitlab(dict2obj({
            'id': 2,
            'body': f'added 1h 1m of time spent at {date.today():{GITLAB_DATE_FORMAT}}',
            'created_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
            'updated_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
            'author': {
                'id': self.user.gl_id
            }
        }), self.issue)

        self.assertEqual(Note.objects.count(), 2)

    def test_load_spend_has_after(self):
        Note.objects.create(
            gl_id=3,
            content_object=self.issue,
            user=self.user,
            created_at=timezone.now(),
            data={}
        )

        self.assertEqual(Note.objects.count(), 1)

        Note.objects.sync_gitlab(dict2obj({
            'id': 2,
            'body': f'added 1h 1m of time spent at {date.today():{GITLAB_DATE_FORMAT}}',
            'created_at': datetime.strftime(timezone.now() - timedelta(hours=1), GITLAB_DATETIME_FORMAT),
            'updated_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
            'author': {
                'id': self.user.gl_id
            }
        }), self.issue)

        self.assertEqual(Note.objects.count(), 1)
