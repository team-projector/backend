from datetime import datetime

from django.test import TestCase

from apps.core.gitlab import GITLAB_DATETIME_FORMAT
from apps.core.utils.objects import dict2obj
from apps.development.models import Note
from apps.development.models.note import NOTE_TYPES
from apps.users.models import User
from tests.test_development.factories import IssueFactory


class MovedFromNoteTypeTests(TestCase):
    def setUp(self):
        self.issue = IssueFactory.create()
        self.user = User.objects.create_user(
            login='user',
            gl_id=10
        )

    def test_success(self):
        body = 'moved from group/project#111'

        Note.objects.update_from_gitlab(dict2obj({
            'id': 2,
            'body': body,
            'created_at': datetime.strftime(
                datetime.now(),
                GITLAB_DATETIME_FORMAT,
            ),
            'updated_at': datetime.strftime(
                datetime.now(),
                GITLAB_DATETIME_FORMAT,
            ),
            'author': {
                'id': self.user.gl_id
            },
            'system': True
        }), self.issue)

        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.first()
        self.assertEqual(note.gl_id, 2)
        self.assertEqual(note.user, self.user)
        self.assertEqual(note.type, NOTE_TYPES.MOVED_FROM)
        self.assertEqual(note.body, body)

    def test_no_system(self):
        body = 'moved from group/project#111'

        Note.objects.update_from_gitlab(dict2obj({
            'id': 2,
            'body': body,
            'created_at': datetime.strftime(
                datetime.now(),
                GITLAB_DATETIME_FORMAT,
            ),
            'updated_at': datetime.strftime(
                datetime.now(),
                GITLAB_DATETIME_FORMAT,
            ),
            'author': {
                'id': self.user.gl_id
            },
            'system': False
        }), self.issue)

        self.assertFalse(Note.objects.exists())

    def test_bad_issue_number(self):
        body = 'moved from group/project#111b'

        Note.objects.update_from_gitlab(dict2obj({
            'id': 2,
            'body': body,
            'created_at': datetime.strftime(
                datetime.now(),
                GITLAB_DATETIME_FORMAT,
            ),
            'updated_at': datetime.strftime(
                datetime.now(),
                GITLAB_DATETIME_FORMAT,
            ),
            'author': {
                'id': self.user.gl_id
            },
            'system': True
        }), self.issue)

        self.assertFalse(Note.objects.exists())
