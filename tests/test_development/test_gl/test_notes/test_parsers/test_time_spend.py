from datetime import date, datetime, timedelta

from django.utils import timezone
from jnt_django_toolbox.helpers.objects import dict2obj
from jnt_django_toolbox.helpers.time import seconds

from apps.core.gitlab.parsers import GITLAB_DATE_FORMAT, GITLAB_DATETIME_FORMAT
from apps.development.models import Note
from apps.development.models.note import NoteType
from apps.development.services.note.gl.parsers.spend_reset import (
    SPEND_RESET_MESSAGE,
)
from apps.development.services.note.gl.sync import update_note_from_gitlab
from tests.helpers.checkers import assert_instance_fields
from tests.test_development.factories import IssueFactory

KEY_ID = "id"
KEY_AUTHOR = "author"
KEY_BODY = "body"
KEY_CREATED_AT = "created_at"
KEY_UPDATED_AT = "updated_at"

BODY_TEMPLATE = "added 1h 1m of time spent at {0}"


def test_added(user):
    """
    Test added.

    :param user:
    """
    issue = IssueFactory.create()
    date_str = date.today().strftime(GITLAB_DATE_FORMAT)

    body = BODY_TEMPLATE.format(date_str)

    update_note_from_gitlab(
        dict2obj(
            {
                KEY_ID: 2,
                KEY_BODY: body,
                KEY_CREATED_AT: datetime.strftime(
                    datetime.now(),
                    GITLAB_DATETIME_FORMAT,
                ),
                KEY_UPDATED_AT: datetime.strftime(
                    datetime.now(),
                    GITLAB_DATETIME_FORMAT,
                ),
                KEY_AUTHOR: {KEY_ID: user.gl_id},
            },
        ),
        issue,
    )

    assert Note.objects.count() == 1

    note = Note.objects.first()
    assert note.data["spent"] == seconds(hours=1, minutes=1)
    assert note.data["date"] == date_str
    assert_instance_fields(
        note,
        gl_id=2,
        user=user,
        type=NoteType.TIME_SPEND,
        body=body,
    )


def test_subtracted(user):
    """
    Test subtracted.

    :param user:
    """
    issue = IssueFactory.create()
    date_str = date.today().strftime(GITLAB_DATE_FORMAT)

    body = "subtracted 1h 1m of time spent at {0}".format(date_str)
    update_note_from_gitlab(
        dict2obj(
            {
                KEY_ID: 2,
                KEY_BODY: body,
                KEY_CREATED_AT: datetime.strftime(
                    datetime.now(),
                    GITLAB_DATETIME_FORMAT,
                ),
                KEY_UPDATED_AT: datetime.strftime(
                    datetime.now(),
                    GITLAB_DATETIME_FORMAT,
                ),
                KEY_AUTHOR: {KEY_ID: user.gl_id},
            },
        ),
        issue,
    )

    assert Note.objects.count() == 1

    note = Note.objects.first()
    assert note.data["spent"] == -seconds(hours=1, minutes=1)
    assert note.data["date"] == date_str
    assert_instance_fields(
        note,
        gl_id=2,
        user=user,
        type=NoteType.TIME_SPEND,
        body=body,
    )


def test_removed(user):
    """
    Test removed.

    :param user:
    """
    issue = IssueFactory.create()

    update_note_from_gitlab(
        dict2obj(
            {
                KEY_ID: 2,
                KEY_BODY: SPEND_RESET_MESSAGE,
                KEY_CREATED_AT: datetime.strftime(
                    datetime.now(),
                    GITLAB_DATETIME_FORMAT,
                ),
                KEY_UPDATED_AT: datetime.strftime(
                    datetime.now(),
                    GITLAB_DATETIME_FORMAT,
                ),
                KEY_AUTHOR: {KEY_ID: user.gl_id},
            },
        ),
        issue,
    )

    assert Note.objects.count() == 1

    note = Note.objects.first()

    assert not note.data
    assert_instance_fields(
        note,
        gl_id=2,
        user=user,
        type=NoteType.RESET_SPEND,
        body=SPEND_RESET_MESSAGE,
    )


def test_already_exists(user):
    """
    Test already exists.

    :param user:
    """
    issue = IssueFactory.create()

    Note.objects.create(gl_id=2, content_object=issue, user=user, data={})

    update_note_from_gitlab(
        dict2obj(
            {
                KEY_ID: 2,
                KEY_BODY: BODY_TEMPLATE.format(
                    date.today().strftime(GITLAB_DATE_FORMAT),
                ),
                KEY_CREATED_AT: datetime.strftime(
                    datetime.now(),
                    GITLAB_DATETIME_FORMAT,
                ),
                KEY_UPDATED_AT: datetime.strftime(
                    datetime.now(),
                    GITLAB_DATETIME_FORMAT,
                ),
                KEY_AUTHOR: {KEY_ID: user.gl_id},
            },
        ),
        issue,
    )

    assert Note.objects.count() == 1

    note = Note.objects.first()
    assert note.gl_id == 2
    assert note.user == user


def test_already_has_another(user):
    """
    Test already has another.

    :param user:
    """
    issue = IssueFactory.create()

    Note.objects.create(gl_id=3, content_object=issue, user=user, data={})

    update_note_from_gitlab(
        dict2obj(
            {
                KEY_ID: 2,
                KEY_BODY: BODY_TEMPLATE.format(
                    date.today().strftime(GITLAB_DATE_FORMAT),
                ),
                KEY_CREATED_AT: datetime.strftime(
                    datetime.now(),
                    GITLAB_DATETIME_FORMAT,
                ),
                KEY_UPDATED_AT: datetime.strftime(
                    datetime.now(),
                    GITLAB_DATETIME_FORMAT,
                ),
                KEY_AUTHOR: {KEY_ID: user.gl_id},
            },
        ),
        issue,
    )

    assert Note.objects.count() == 2


def test_has_prior(user):
    """
    Test has prior.

    :param user:
    """
    issue = IssueFactory.create()

    Note.objects.create(
        gl_id=3,
        content_object=issue,
        user=user,
        created_at=timezone.now() - timedelta(hours=1),
        data={},
    )

    update_note_from_gitlab(
        dict2obj(
            {
                KEY_ID: 2,
                KEY_BODY: BODY_TEMPLATE.format(
                    date.today().strftime(GITLAB_DATE_FORMAT),
                ),
                KEY_CREATED_AT: datetime.strftime(
                    datetime.now(),
                    GITLAB_DATETIME_FORMAT,
                ),
                KEY_UPDATED_AT: datetime.strftime(
                    datetime.now(),
                    GITLAB_DATETIME_FORMAT,
                ),
                KEY_AUTHOR: {KEY_ID: user.gl_id},
            },
        ),
        issue,
    )

    assert Note.objects.count() == 2


def test_body_without_date(user):
    """
    Test body without date.

    :param user:
    """
    issue = IssueFactory.create()

    note_date = date.today()

    body = "added 1h 1m of time spent"

    update_note_from_gitlab(
        dict2obj(
            {
                KEY_ID: 2,
                KEY_BODY: body,
                KEY_CREATED_AT: datetime.strftime(
                    datetime.now(),
                    GITLAB_DATETIME_FORMAT,
                ),
                KEY_UPDATED_AT: datetime.strftime(
                    datetime.now(),
                    GITLAB_DATETIME_FORMAT,
                ),
                KEY_AUTHOR: {KEY_ID: user.gl_id},
            },
        ),
        issue,
    )

    assert Note.objects.count() == 1

    note = Note.objects.first()

    assert note.data["spent"] == seconds(hours=1, minutes=1)
    assert note.data["date"] == note_date.strftime(GITLAB_DATE_FORMAT)

    assert_instance_fields(
        note,
        gl_id=2,
        user=user,
        type=NoteType.TIME_SPEND,
        body=body,
    )
