# -*- coding: utf-8 -*-

from datetime import datetime

from apps.core.gitlab import GITLAB_DATETIME_FORMAT
from apps.core.utils.objects import dict2obj
from apps.development.models import Note
from tests.test_development.factories import IssueFactory


def test_unsupported(user):
    issue = IssueFactory.create()
    Note.objects.update_from_gitlab(dict2obj({
        'id': 2,
        'body': 'bla',
        'created_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
        'updated_at': datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
        'author': {
            'id': user.gl_id
        }
    }), issue)

    assert not Note.objects.exists()
