from datetime import datetime

from django.test import TestCase

from apps.core.utils.objects import dict2obj
from apps.development.models import Note
from apps.development.services.parsers import GITLAB_DATETIME_FORMAT
from apps.users.models import User
from tests.test_development.factories import IssueFactory


class UnknownNoteTypeTests(TestCase):
    def setUp(self):
        self.issue = IssueFactory.create()
        self.user = User.objects.create_user(login='user', gl_id=10)

    def test_load_unsupported(self):
        Note.objects.update_from_gitlab(dict2obj({
            'id': 2,
            'body': 'bla',
            'created_at': datetime.strftime(datetime.now(),
                                            GITLAB_DATETIME_FORMAT),
            'updated_at': datetime.strftime(datetime.now(),
                                            GITLAB_DATETIME_FORMAT),
            'author': {
                'id': self.user.gl_id
            }
        }), self.issue)

        self.assertFalse(Note.objects.exists())
