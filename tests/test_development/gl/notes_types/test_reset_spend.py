from datetime import datetime

from django.test import TestCase

from apps.core.utils.objects import dict2obj
from apps.development.models import Note
from apps.development.models.note import NOTE_TYPES
from apps.development.services.gitlab.notes import SPEND_RESET_MESSAGE
from apps.development.services.parsers import GITLAB_DATETIME_FORMAT
from apps.users.models import User
from tests.test_development.factories import IssueFactory


class ResetSpendNoteType(TestCase):
    def setUp(self):
        self.issue = IssueFactory.create()
        self.user = User.objects.create_user(login='user', gl_id=10)

    def test_load_spend_reset(self):
        Note.objects.sync_gitlab(dict2obj({
            'id': 2,
            'body': SPEND_RESET_MESSAGE,
            'created_at': datetime.strftime(datetime.now(),
                                            GITLAB_DATETIME_FORMAT),
            'updated_at': datetime.strftime(datetime.now(),
                                            GITLAB_DATETIME_FORMAT),
            'author': {
                'id': self.user.gl_id
            }
        }), self.issue)

        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.first()
        self.assertEqual(note.gl_id, 2)
        self.assertEqual(note.user, self.user)
        self.assertEqual(note.body, SPEND_RESET_MESSAGE)
        self.assertEqual(note.type, NOTE_TYPES.reset_spend)
        self.assertEqual(note.data, {})
