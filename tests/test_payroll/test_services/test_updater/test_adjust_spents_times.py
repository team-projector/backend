from datetime import datetime

import pytest
from jnt_django_toolbox.helpers.time import seconds

from apps.development.models import Issue
from apps.development.models.note import NoteType
from apps.payroll.models import SpentTime
from apps.payroll.services.spent_time.updater import adjust_spents_times
from tests.test_development.factories import (
    IssueNoteFactory,
    MergeRequestNoteFactory,
)
from tests.test_payroll.factories import IssueSpentTimeFactory

NOTE_TYPE_PARAMS = (
    (NoteType.TIME_SPEND, 1),
    (NoteType.RESET_SPEND, 1),
    (NoteType.MOVED_FROM, 0),
    (NoteType.COMMENT, 0),
)


@pytest.fixture(params=[IssueNoteFactory, MergeRequestNoteFactory])
def user_note(user, request):
    """Generate user note."""
    return request.param.create(
        type=NoteType.TIME_SPEND,
        user=user,
        data={"date": str(datetime.now().date()), "spent": seconds(hours=2)},
    )


@pytest.mark.parametrize(
    ("note_type", "spent_time_count"),
    NOTE_TYPE_PARAMS,
)
def test_adjust_spents_times(user_note, note_type, spent_time_count):
    """Test adjust spent times."""
    user_note.type = note_type  # noqa: WPS125
    user_note.save()

    spent_times = SpentTime.objects.all()

    assert not spent_times.exists()

    adjust_spents_times()
    assert spent_times.count() == spent_time_count


@pytest.mark.parametrize(
    ("note_type", "spent_time_count"),
    NOTE_TYPE_PARAMS,
)
def test_adjust_spents_times_twice(user_note, note_type, spent_time_count):
    """Test adjust spent times twice."""
    user_note.type = note_type  # noqa: WPS125
    user_note.save()

    spent_times = SpentTime.objects.all()

    assert not spent_times.exists()

    adjust_spents_times()
    adjust_spents_times()

    assert spent_times.count() == spent_time_count


def test_spent_time_exists(user):
    """Test not create spent time if exists."""
    note = IssueNoteFactory.create(type=NoteType.TIME_SPEND, user=user)
    issue = Issue.objects.first()

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        note=note,
        time_spent=0,
    )
    spent_times = SpentTime.objects.all()

    assert spent_times.count() == 1

    adjust_spents_times()

    assert spent_times.count() == 1


def test_not_trackable_note(user):
    """Test not trackable note."""
    IssueNoteFactory.create(
        content_object=user,
        type=NoteType.TIME_SPEND,
        user=user,
        data={"date": str(datetime.now().date()), "spent": seconds(hours=2)},
    )

    spent_times = SpentTime.objects.all()

    assert not spent_times.exists()

    adjust_spents_times()

    assert not spent_times.exists()
