from collections import defaultdict
from datetime import datetime, timedelta

from django.utils import timezone

from apps.core.gitlab import parse_gl_date
from apps.development.models.note import NOTE_TYPES
from apps.payroll.models import SpentTime
from tests.test_development.factories import IssueFactory, IssueNoteFactory
from tests.test_users.factories import UserFactory


def test_parse_date():
    assert parse_gl_date('') is None
    assert parse_gl_date('2000-01-01') == datetime(2000, 1, 1).date()


def test_simple(user):
    issue = IssueFactory.create()

    _create_note(user, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=2),
                 timedelta(hours=1))
    _create_note(user, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=1),
                 timedelta(hours=5))
    _create_note(user, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=1),
                 -timedelta(hours=3))
    _create_note(user, issue,
                 NOTE_TYPES.reset_spend,
                 timezone.now() - timedelta(minutes=30))

    issue.adjust_spent_times()

    _check_generated_time_spents(issue)


def test_different_created_at_and_date(user):
    issue = IssueFactory.create()

    _create_note(user, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=2),
                 timedelta(hours=1),
                 date=(timezone.now() - timedelta(days=1)).date())
    _create_note(user, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=1),
                 timedelta(hours=5),
                 date=(timezone.now() - timedelta(days=2)).date())
    _create_note(user, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=1),
                 -timedelta(hours=3),
                 date=(timezone.now() - timedelta(days=3)).date())
    _create_note(user, issue,
                 NOTE_TYPES.reset_spend,
                 timezone.now() - timedelta(minutes=30),
                 date=(timezone.now() - timedelta(days=5)).date())

    issue.adjust_spent_times()

    _check_generated_time_spents(issue)


def test_many_resets(user):
    issue = IssueFactory.create()

    _create_note(user, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=2),
                 timedelta(hours=1))
    _create_note(user, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=1),
                 timedelta(hours=5))
    _create_note(user, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=1),
                 -timedelta(hours=3))
    _create_note(user, issue,
                 NOTE_TYPES.reset_spend,
                 timezone.now() - timedelta(minutes=30))

    _create_note(user, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=5),
                 -timedelta(hours=3))
    _create_note(user, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=6),
                 timedelta(hours=4))

    issue.adjust_spent_times()
    _check_generated_time_spents(issue)


def test_only_reset(user):
    issue = IssueFactory.create()

    _create_note(user, issue,
                 NOTE_TYPES.reset_spend,
                 timezone.now() - timedelta(minutes=30))

    issue.adjust_spent_times()

    _check_generated_time_spents(issue)


def test_multi_user_reset(user):
    issue = IssueFactory.create()

    user_2 = UserFactory.create()

    _create_note(user_2, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=6),
                 timedelta(hours=4))
    _create_note(user_2, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=5),
                 -timedelta(hours=3))
    _create_note(user_2, issue,
                 NOTE_TYPES.reset_spend,
                 timezone.now() - timedelta(hours=4))

    _create_note(user, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=4),
                 timedelta(hours=5))
    _create_note(user, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=2),
                 timedelta(hours=1))
    _create_note(user, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=1),
                 timedelta(hours=5))
    _create_note(user, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=1),
                 -timedelta(hours=3))
    _create_note(user, issue,
                 NOTE_TYPES.reset_spend,
                 timezone.now() - timedelta(minutes=30))

    _create_note(user_2, issue,
                 NOTE_TYPES.time_spend,
                 timezone.now() - timedelta(hours=1),
                 timedelta(hours=5))
    _create_note(user_2, issue,
                 NOTE_TYPES.reset_spend,
                 timezone.now() - timedelta(minutes=30))

    issue.adjust_spent_times()

    _check_generated_time_spents(issue)


def test_spents_but_moved_from(user):
    issue = IssueFactory.create()

    spent_before = _create_note(user, issue,
                                NOTE_TYPES.time_spend,
                                timezone.now() - timedelta(hours=2),
                                timedelta(hours=1))

    moved_from = _create_note(user, issue,
                              NOTE_TYPES.moved_from,
                              timezone.now() - timedelta(hours=1))

    spent_after = _create_note(user, issue,
                               NOTE_TYPES.time_spend,
                               timezone.now() - timedelta(minutes=30),
                               timedelta(hours=5))

    issue.adjust_spent_times()

    assert SpentTime.objects.filter(note=spent_before).exists() is False
    assert SpentTime.objects.filter(note=moved_from).exists() is False
    assert SpentTime.objects.filter(note=spent_after).exists() is True


def test_spents_with_resets_but_moved_from(user):
    issue = IssueFactory.create()

    spent_before = _create_note(user, issue,
                                NOTE_TYPES.time_spend,
                                timezone.now() - timedelta(hours=2),
                                timedelta(hours=1))

    moved_from = _create_note(user, issue,
                              NOTE_TYPES.moved_from,
                              timezone.now() - timedelta(hours=1))

    spent_after = _create_note(user, issue,
                               NOTE_TYPES.time_spend,
                               timezone.now() - timedelta(minutes=30),
                               timedelta(hours=5))

    reset_spend = _create_note(user, issue,
                               NOTE_TYPES.reset_spend,
                               timezone.now() - timedelta(minutes=15))

    issue.adjust_spent_times()

    assert SpentTime.objects.filter(note=spent_before).exists() is False
    assert SpentTime.objects.filter(note=moved_from).exists() is False
    assert SpentTime.objects.filter(note=spent_after).exists() is True

    reset_spent_time = SpentTime.objects.filter(note=reset_spend).first()
    assert reset_spent_time is not None
    assert -timedelta(hours=5).total_seconds() == reset_spent_time.time_spent


def _create_note(user, issue, note_type, created_at,
                 spent: timedelta = None, date=None, ):
    return IssueNoteFactory.create(
        type=note_type,
        created_at=created_at,
        updated_at=created_at,
        user=user,
        content_object=issue,
        data={
            'spent': spent.total_seconds(),
            'date': date or created_at.date()
        } if spent else {}
    )


def _check_generated_time_spents(issue):
    users_spents = defaultdict(int)

    for note in issue.notes.all().order_by('created_at'):
        spent_time = SpentTime.objects.filter(note=note).first()

        assert spent_time is not None

        if note.type == NOTE_TYPES.reset_spend:
            assert spent_time.time_spent == -users_spents[note.user_id]
            users_spents[note.user_id] = 0
        elif note.type == NOTE_TYPES.time_spend:
            assert spent_time.time_spent == note.data['spent']
            assert spent_time.date == parse_gl_date(note.data['date'])
            users_spents[note.user_id] += note.data['spent']
