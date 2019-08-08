from datetime import timedelta

from apps.development.models import MergeRequest
from apps.development.models.issue import STATE_OPENED, STATE_CLOSED
from apps.payroll.models import SpentTime
from apps.payroll.services.summary.spent_times import \
    get_spent_times_summary
from tests.test_development.factories import (
    IssueFactory, MergeRequestFactory
)
from tests.test_payroll.factories import (
    IssueSpentTimeFactory, MergeRequestSpentTimeFactory
)


def test_without_spents(user):
    IssueFactory.create_batch(
        5, user=user,
        state=STATE_OPENED,
        total_time_spent=1000
    )
    MergeRequestFactory.create_batch(
        5, user=user,
        state=MergeRequest.STATE.opened,
        total_time_spent=1000
    )

    summary = get_spent_times_summary(
        SpentTime.objects.all(),
        project=None,
        team=None,
        user=None
    )

    assert summary.issues.issues_count == 0
    assert summary.issues.spent == 0

    assert summary.merge_requests.count == 0
    assert summary.merge_requests.spent == 0


def test_issues_spents(user):
    issue_opened = IssueFactory.create(user=user, state=STATE_OPENED)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue_opened,
        time_spent=timedelta(hours=2).total_seconds()
    )

    IssueSpentTimeFactory.create(
        user=user,
        base=issue_opened,
        time_spent=timedelta(hours=3).total_seconds()
    )

    issue_closed = IssueFactory.create(user=user, state=STATE_CLOSED)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue_closed,
        time_spent=timedelta(hours=2).total_seconds()
    )

    IssueSpentTimeFactory.create(
        user=user,
        base=issue_closed,
        time_spent=timedelta(hours=1).total_seconds()
    )

    summary = get_spent_times_summary(
        SpentTime.objects.all(),
        project=None,
        team=None,
        user=None
    )

    assert summary.issues.issues_count == 2
    assert summary.issues.opened_count == 1
    assert summary.issues.spent == timedelta(hours=8).total_seconds()

    assert summary.merge_requests.count == 0
    assert summary.merge_requests.spent == 0

    assert summary.spent == timedelta(hours=8).total_seconds()


def test_merge_requests_spents(user):
    mr_opened = MergeRequestFactory.create(user=user,
                                           state=MergeRequest.STATE.opened)

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr_opened,
        time_spent=timedelta(hours=2).total_seconds()
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr_opened,
        time_spent=timedelta(hours=3).total_seconds()
    )

    mr_closed = MergeRequestFactory.create(user=user,
                                           state=MergeRequest.STATE.closed)

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr_closed,
        time_spent=timedelta(hours=2).total_seconds()
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr_closed,
        time_spent=timedelta(hours=1).total_seconds()
    )

    mr_merged = MergeRequestFactory.create(user=user,
                                           state=MergeRequest.STATE.merged)

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr_merged,
        time_spent=timedelta(hours=1).total_seconds()
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr_merged,
        time_spent=timedelta(hours=4).total_seconds()
    )

    summary = get_spent_times_summary(
        SpentTime.objects.all(),
        project=None,
        team=None,
        user=None
    )

    assert summary.issues.issues_count == 0
    assert summary.issues.opened_count == 0
    assert summary.issues.spent == 0

    assert summary.merge_requests.count == 3
    assert summary.merge_requests.opened_count == 1
    assert summary.merge_requests.closed_count == 1
    assert summary.merge_requests.merged_count == 1
    assert summary.merge_requests.spent == timedelta(hours=13).total_seconds()

    assert summary.spent == timedelta(hours=13).total_seconds()


def test_complex_spents(user):
    issue = IssueFactory.create(user=user, state=STATE_OPENED)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=timedelta(hours=2).total_seconds()
    )

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=timedelta(hours=3).total_seconds()
    )

    merge_request = MergeRequestFactory.create(user=user,
                                               state=MergeRequest.STATE.opened)

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=merge_request,
        time_spent=timedelta(hours=1).total_seconds()
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=merge_request,
        time_spent=timedelta(hours=2).total_seconds()
    )

    summary = get_spent_times_summary(
        SpentTime.objects.all(),
        project=None,
        team=None,
        user=None
    )

    assert summary.issues.issues_count == 1
    assert summary.issues.spent == timedelta(hours=5).total_seconds()

    assert summary.merge_requests.count == 1
    assert summary.merge_requests.spent == timedelta(hours=3).total_seconds()

    assert summary.spent == timedelta(hours=8).total_seconds()
