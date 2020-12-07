from collections import defaultdict
from datetime import timedelta

from django.utils import timezone

from apps.core.gitlab import parse_gl_date
from apps.development.models.note import NoteType
from apps.payroll.models import SpentTime
from apps.payroll.services.spent_time.updater import adjust_spent_times
from tests.test_development.factories import IssueFactory, IssueNoteFactory
from tests.test_users.factories.user import UserFactory


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
