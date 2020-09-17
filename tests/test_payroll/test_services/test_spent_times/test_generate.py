# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import datetime, timedelta

from django.utils import timezone

from apps.core.gitlab import parse_gl_date
from apps.development.models.note import NoteType
from apps.payroll.models import SpentTime
from apps.payroll.services.spent_time.updater import adjust_spent_times
from tests.test_development.factories import IssueFactory, IssueNoteFactory
from tests.test_users.factories.user import UserFactory


def test_parse_date():
    """Test parse date."""
    assert parse_gl_date("") is None
    assert parse_gl_date("2000-01-01") == datetime(2000, 1, 1).date()


def test_simple(user):
    """
    Test simple.

    :param user:
    """
    issue = IssueFactory.create()

    _create_note(
        user,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=2),
        timedelta(hours=1),
    )
    _create_note(
        user,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=1),
        timedelta(hours=5),
    )
    _create_note(
        user,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=1),
        -timedelta(hours=3),
    )
    _create_note(
        user,
        issue,
        NoteType.RESET_SPEND,
        timezone.now() - timedelta(minutes=30),
    )

    adjust_spent_times(issue)

    _check_generated_time_spents(issue)


def test_different_created_at_and_date(user):
    """
    Test different created at and date.

    :param user:
    """
    issue = IssueFactory.create()

    _create_note(
        user,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=2),
        timedelta(hours=1),
        date=(timezone.now() - timedelta(days=1)).date(),
    )
    _create_note(
        user,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=1),
        timedelta(hours=5),
        date=(timezone.now() - timedelta(days=2)).date(),
    )
    _create_note(
        user,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=1),
        -timedelta(hours=3),
        date=(timezone.now() - timedelta(days=3)).date(),
    )
    _create_note(
        user,
        issue,
        NoteType.RESET_SPEND,
        timezone.now() - timedelta(minutes=30),
        date=(timezone.now() - timedelta(days=5)).date(),
    )

    adjust_spent_times(issue)

    _check_generated_time_spents(issue)


def test_many_resets(user):
    """
    Test many resets.

    :param user:
    """
    issue = IssueFactory.create()

    _create_note(
        user,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=2),
        timedelta(hours=1),
    )
    _create_note(
        user,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=1),
        timedelta(hours=5),
    )
    _create_note(
        user,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=1),
        -timedelta(hours=3),
    )
    _create_note(
        user,
        issue,
        NoteType.RESET_SPEND,
        timezone.now() - timedelta(minutes=30),
    )

    _create_note(
        user,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=5),
        -timedelta(hours=3),
    )
    _create_note(
        user,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=6),
        timedelta(hours=4),
    )

    adjust_spent_times(issue)
    _check_generated_time_spents(issue)


def test_only_reset(user):
    """
    Test only reset.

    :param user:
    """
    issue = IssueFactory.create()

    _create_note(
        user,
        issue,
        NoteType.RESET_SPEND,
        timezone.now() - timedelta(minutes=30),
    )

    adjust_spent_times(issue)

    _check_generated_time_spents(issue)


def test_multi_user_reset(user):
    """
    Test multi user reset.

    :param user:
    """
    issue = IssueFactory.create()

    user2 = UserFactory.create()

    _create_note(
        user2,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=6),
        timedelta(hours=4),
    )
    _create_note(
        user2,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=5),
        -timedelta(hours=3),
    )
    _create_note(
        user2,
        issue,
        NoteType.RESET_SPEND,
        timezone.now() - timedelta(hours=4),
    )

    _create_note(
        user,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=4),
        timedelta(hours=5),
    )
    _create_note(
        user,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=2),
        timedelta(hours=1),
    )
    _create_note(
        user,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=1),
        timedelta(hours=5),
    )
    _create_note(
        user,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=1),
        -timedelta(hours=3),
    )
    _create_note(
        user,
        issue,
        NoteType.RESET_SPEND,
        timezone.now() - timedelta(minutes=30),
    )

    _create_note(
        user2,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=1),
        timedelta(hours=5),
    )
    _create_note(
        user2,
        issue,
        NoteType.RESET_SPEND,
        timezone.now() - timedelta(minutes=30),
    )

    adjust_spent_times(issue)

    _check_generated_time_spents(issue)


def test_spents_but_moved_from(user):
    """
    Test spents but moved from.

    :param user:
    """
    issue = IssueFactory.create()

    spent_before = _create_note(
        user,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(hours=2),
        timedelta(hours=1),
    )

    moved_from = _create_note(
        user,
        issue,
        NoteType.MOVED_FROM,
        timezone.now() - timedelta(hours=1),
    )

    spent_after = _create_note(
        user,
        issue,
        NoteType.TIME_SPEND,
        timezone.now() - timedelta(minutes=30),
        timedelta(hours=5),
    )

    adjust_spent_times(issue)

    assert not SpentTime.objects.filter(note=spent_before).exists()
    assert not SpentTime.objects.filter(note=moved_from).exists()
    assert SpentTime.objects.filter(note=spent_after).exists()


def test_spents_with_resets_but_moved_from(user):
    """
    Test spents with resets but moved from.

    :param user:
    """
    issue = IssueFactory.create()

    notes = [
        _create_note(
            user,
            issue,
            NoteType.TIME_SPEND,
            timezone.now() - timedelta(hours=2),
            timedelta(hours=1),
        ),
        _create_note(
            user,
            issue,
            NoteType.MOVED_FROM,
            timezone.now() - timedelta(hours=1),
        ),
        _create_note(
            user,
            issue,
            NoteType.TIME_SPEND,
            timezone.now() - timedelta(minutes=30),
            timedelta(hours=5),
        ),
        _create_note(
            user,
            issue,
            NoteType.RESET_SPEND,
            timezone.now() - timedelta(minutes=15),
        ),
    ]

    adjust_spent_times(issue)

    assert not SpentTime.objects.filter(note=notes[0]).exists()
    assert not SpentTime.objects.filter(note=notes[1]).exists()
    assert SpentTime.objects.filter(note=notes[2]).exists()

    reset_spent_time = SpentTime.objects.filter(note=notes[3]).first()
    assert reset_spent_time is not None
    assert reset_spent_time.time_spent == -timedelta(hours=5).total_seconds()


def _create_note(  # noqa: WPS211
    user,
    issue,
    note_type,
    created_at,
    spent: timedelta = None,
    date=None,
):
    """
    Create note.

    :param user:
    :param issue:
    :param note_type:
    :param created_at:
    :param spent:
    :type spent: timedelta, optional
    :param date:
    """
    return IssueNoteFactory.create(
        type=note_type,
        created_at=created_at,
        updated_at=created_at,
        user=user,
        content_object=issue,
        data={
            "spent": spent.total_seconds(),
            "date": date or created_at.date(),
        }
        if spent
        else {},
    )


def _check_generated_time_spents(issue):
    """
    Check generated time spents.

    :param issue:
    """
    users_spents = defaultdict(int)

    for note in issue.notes.all().order_by("created_at"):
        spent_time = SpentTime.objects.filter(note=note).first()

        assert spent_time is not None

        if note.type == NoteType.RESET_SPEND:
            assert spent_time.time_spent == -users_spents[note.user_id]
            users_spents[note.user_id] = 0
        elif note.type == NoteType.TIME_SPEND:
            assert spent_time.time_spent == note.data["spent"]
            assert spent_time.date == parse_gl_date(note.data["date"])
            users_spents[note.user_id] += note.data["spent"]
