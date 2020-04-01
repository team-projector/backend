# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta

from django.utils import timezone

from apps.core.gitlab.parsers import GITLAB_DATE_FORMAT, GITLAB_DATETIME_FORMAT
from apps.core.utils.objects import dict2obj
from apps.core.utils.time import seconds
from apps.development.models import Note
from apps.development.models.note import NoteType
from apps.development.services.note.notes_parsers.base import (
    SPEND_RESET_MESSAGE,
)
from tests.test_development.factories import IssueFactory


def test_added(user):
    issue = IssueFactory.create()
    date_str = date.today().strftime(GITLAB_DATE_FORMAT)

    body = "added 1h 1m of time spent at {0}".format(date_str)

    Note.objects.update_from_gitlab(
        dict2obj(
            {
                "id": 2,
                "body": body,
                "created_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "updated_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "author": {"id": user.gl_id},
            },
        ),
        issue,
    )

    assert Note.objects.count() == 1

    note = Note.objects.first()
    assert note.gl_id == 2
    assert note.user == user
    assert note.type == NoteType.TIME_SPEND
    assert note.body == body
    assert note.data["spent"] == seconds(hours=1, minutes=1)
    assert note.data["date"] == date_str


def test_subtracted(user):
    issue = IssueFactory.create()
    date_str = date.today().strftime(GITLAB_DATE_FORMAT)

    body = "subtracted 1h 1m of time spent at {0}".format(date_str)
    Note.objects.update_from_gitlab(
        dict2obj(
            {
                "id": 2,
                "body": body,
                "created_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "updated_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "author": {"id": user.gl_id},
            },
        ),
        issue,
    )

    assert Note.objects.count() == 1

    note = Note.objects.first()
    assert note.gl_id == 2
    assert note.user == user
    assert note.body == body
    assert note.type == NoteType.TIME_SPEND
    assert note.data["spent"] == -seconds(hours=1, minutes=1)
    assert note.data["date"] == date_str


def test_removed(user):
    issue = IssueFactory.create()

    Note.objects.update_from_gitlab(
        dict2obj(
            {
                "id": 2,
                "body": SPEND_RESET_MESSAGE,
                "created_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "updated_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "author": {"id": user.gl_id},
            },
        ),
        issue,
    )

    assert Note.objects.count() == 1

    note = Note.objects.first()
    assert note.gl_id == 2
    assert note.user == user
    assert note.body == SPEND_RESET_MESSAGE
    assert note.type == NoteType.RESET_SPEND
    assert not note.data


def test_already_exists(user):
    issue = IssueFactory.create()

    Note.objects.create(gl_id=2, content_object=issue, user=user, data={})

    Note.objects.update_from_gitlab(
        dict2obj(
            {
                "id": 2,
                "body": "added 1h 1m of time spent at {0}".format(
                    date.today().strftime(GITLAB_DATE_FORMAT),
                ),
                "created_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "updated_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "author": {"id": user.gl_id},
            },
        ),
        issue,
    )

    assert Note.objects.count() == 1

    note = Note.objects.first()
    assert note.gl_id == 2
    assert note.user == user


def test_already_has_another(user):
    issue = IssueFactory.create()

    Note.objects.create(gl_id=3, content_object=issue, user=user, data={})

    Note.objects.update_from_gitlab(
        dict2obj(
            {
                "id": 2,
                "body": "added 1h 1m of time spent at {0}".format(
                    date.today().strftime(GITLAB_DATE_FORMAT),
                ),
                "created_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "updated_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "author": {"id": user.gl_id},
            },
        ),
        issue,
    )

    assert Note.objects.count() == 2


def test_has_prior(user):
    issue = IssueFactory.create()

    Note.objects.create(
        gl_id=3,
        content_object=issue,
        user=user,
        created_at=timezone.now() - timedelta(hours=1),
        data={},
    )

    Note.objects.update_from_gitlab(
        dict2obj(
            {
                "id": 2,
                "body": "added 1h 1m of time spent at {0}".format(
                    date.today().strftime(GITLAB_DATE_FORMAT),
                ),
                "created_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "updated_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "author": {"id": user.gl_id},
            },
        ),
        issue,
    )

    assert Note.objects.count() == 2


def test_has_after(user):
    issue = IssueFactory.create()

    Note.objects.create(
        gl_id=3,
        content_object=issue,
        user=user,
        created_at=timezone.now(),
        data={},
    )

    Note.objects.update_from_gitlab(
        dict2obj(
            {
                "id": 2,
                "body": "added 1h 1m of time spent at {0}".format(
                    date.today().strftime(GITLAB_DATE_FORMAT),
                ),
                "created_at": datetime.strftime(
                    timezone.now() - timedelta(hours=1),
                    GITLAB_DATETIME_FORMAT,
                ),
                "updated_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "author": {"id": user.gl_id},
            },
        ),
        issue,
    )

    assert Note.objects.count() == 1


def test_body_without_date(user):
    issue = IssueFactory.create()

    note_date = date.today()

    body = "added 1h 1m of time spent"

    Note.objects.update_from_gitlab(
        dict2obj(
            {
                "id": 2,
                "body": body,
                "created_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "updated_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "author": {"id": user.gl_id},
            },
        ),
        issue,
    )

    assert Note.objects.count() == 1

    note = Note.objects.first()
    assert note.gl_id == 2
    assert note.user == user
    assert note.type == NoteType.TIME_SPEND
    assert note.body == body
    assert note.data["spent"] == seconds(hours=1, minutes=1)
    assert note.data["date"] == note_date.strftime(GITLAB_DATE_FORMAT)
