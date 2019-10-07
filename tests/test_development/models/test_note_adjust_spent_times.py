from datetime import datetime

from apps.core.utils.time import seconds
from apps.development.models import Issue
from apps.development.models.note import NOTE_TYPES
from apps.payroll.models import SpentTime
from tests.test_development.factories import IssueNoteFactory
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_reset_spend(user):
    IssueNoteFactory.create(
        type=NOTE_TYPES.reset_spend,
        user=user,
    )

    assert SpentTime.objects.count() == 0

    issue = Issue.objects.first()
    issue.adjust_spent_times()

    assert SpentTime.objects.count() == 1
    assert SpentTime.objects.first().time_spent == 0


def test_time_spend(user):
    IssueNoteFactory.create(
        type=NOTE_TYPES.time_spend,
        user=user,
        data={
            'date': str(datetime.now().date()),
            'spent': seconds(hours=2)
        },
    )

    assert SpentTime.objects.count() == 0

    issue = Issue.objects.first()
    issue.adjust_spent_times()

    assert SpentTime.objects.count() == 1
    assert SpentTime.objects.first().time_spent == seconds(hours=2)


def test_moved_from(user):
    IssueNoteFactory.create(
        type=NOTE_TYPES.moved_from,
        user=user,
    )

    assert SpentTime.objects.count() == 0

    issue = Issue.objects.first()
    issue.adjust_spent_times()

    assert SpentTime.objects.count() == 0


def test_type_not_exist(user):
    IssueNoteFactory.create(
        type='not_exist',
        user=user,
    )

    issue = Issue.objects.first()
    issue.adjust_spent_times()

    assert SpentTime.objects.count() == 1


def test_spent_time_exists(user):
    note = IssueNoteFactory.create(
        type=NOTE_TYPES.reset_spend,
        user=user,
    )

    issue = Issue.objects.first()

    IssueSpentTimeFactory(
        user=user,
        base=issue,
        note=note,
        time_spent=0,
    )

    assert SpentTime.objects.count() == 1

    issue.adjust_spent_times()

    assert SpentTime.objects.count() == 1
    assert SpentTime.objects.first().time_spent == 0
