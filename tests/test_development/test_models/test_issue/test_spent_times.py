# -*- coding: utf-8 -*-

from datetime import datetime

from jnt_django_toolbox.helpers.time import seconds

from apps.development.models import Issue
from apps.development.models.note import NoteType
from apps.payroll.models import SpentTime
from apps.payroll.services.spent_time.updater import adjust_spent_times
from tests.test_development.factories import IssueNoteFactory
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_reset_spend(user):
    IssueNoteFactory.create(
        type=NoteType.RESET_SPEND, user=user,
    )

    assert SpentTime.objects.count() == 0

    issue = Issue.objects.first()
    adjust_spent_times(issue)

    assert SpentTime.objects.count() == 1
    assert SpentTime.objects.first().time_spent == 0


def test_time_spend(user):
    IssueNoteFactory.create(
        type=NoteType.TIME_SPEND,
        user=user,
        data={"date": str(datetime.now().date()), "spent": seconds(hours=2)},
    )

    assert SpentTime.objects.count() == 0

    issue = Issue.objects.first()
    adjust_spent_times(issue)

    assert SpentTime.objects.count() == 1
    assert SpentTime.objects.first().time_spent == seconds(hours=2)


def test_moved_from(user):
    IssueNoteFactory.create(
        type=NoteType.MOVED_FROM, user=user,
    )

    assert SpentTime.objects.count() == 0

    issue = Issue.objects.first()
    adjust_spent_times(issue)

    assert SpentTime.objects.count() == 0


def test_type_not_exist(user):
    IssueNoteFactory.create(
        type="not_exist", user=user,
    )

    issue = Issue.objects.first()
    adjust_spent_times(issue)

    assert SpentTime.objects.count() == 1


def test_spent_time_exists(user):
    note = IssueNoteFactory.create(type=NoteType.RESET_SPEND, user=user)

    issue = Issue.objects.first()

    IssueSpentTimeFactory(
        user=user, base=issue, note=note, time_spent=0,
    )

    assert SpentTime.objects.count() == 1

    adjust_spent_times(issue)

    assert SpentTime.objects.count() == 1
    assert SpentTime.objects.first().time_spent == 0
