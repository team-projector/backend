from apps.core.utils.time import seconds
from apps.development.models.issue import ISSUE_STATES
from apps.development.models.merge_request import MERGE_REQUESTS_STATES
from apps.payroll.graphql.resolvers import resolve_spent_times_summary
from apps.payroll.models import SpentTime
from apps.payroll.services import spent_time as spent_time_service
from tests.test_development.factories import IssueFactory, MergeRequestFactory
from tests.test_development.factories_gitlab import AttrDict
from tests.test_payroll.factories import (
    IssueSpentTimeFactory, MergeRequestSpentTimeFactory
)


def test_without_spents(user):
    IssueFactory.create_batch(
        5, user=user,
        state=ISSUE_STATES.opened,
        total_time_spent=1000
    )
    MergeRequestFactory.create_batch(
        5, user=user,
        state=MERGE_REQUESTS_STATES.opened,
        total_time_spent=1000
    )

    summary = spent_time_service.get_summary(
        SpentTime.objects.all(),
    )

    assert summary.spent == 0
    assert summary.opened_spent == 0
    assert summary.issues.spent == 0
    assert summary.merge_requests.spent == 0


def test_issues_spents(user):
    issue_opened = IssueFactory.create(user=user, state=ISSUE_STATES.opened)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue_opened,
        time_spent=seconds(hours=2)
    )

    IssueSpentTimeFactory.create(
        user=user,
        base=issue_opened,
        time_spent=seconds(hours=3)
    )

    issue_closed = IssueFactory.create(user=user, state=ISSUE_STATES.closed)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue_closed,
        time_spent=seconds(hours=2)
    )

    IssueSpentTimeFactory.create(
        user=user,
        base=issue_closed,
        time_spent=seconds(hours=1)
    )

    summary = spent_time_service.get_summary(
        SpentTime.objects.all(),
    )

    assert summary.merge_requests.spent == 0

    assert summary.issues.opened_spent == seconds(hours=5)
    assert summary.issues.closed_spent == seconds(hours=3)
    assert summary.issues.spent == seconds(hours=8)

    assert summary.spent == seconds(hours=8)
    assert summary.opened_spent == seconds(hours=5)


def test_merge_requests_spents(user):
    mr_opened = MergeRequestFactory.create(user=user,
                                           state=MERGE_REQUESTS_STATES.opened)

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr_opened,
        time_spent=seconds(hours=2)
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr_opened,
        time_spent=seconds(hours=3)
    )

    mr_closed = MergeRequestFactory.create(user=user,
                                           state=MERGE_REQUESTS_STATES.closed)

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr_closed,
        time_spent=seconds(hours=2)
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr_closed,
        time_spent=seconds(hours=1)
    )

    mr_merged = MergeRequestFactory.create(user=user,
                                           state=MERGE_REQUESTS_STATES.merged)

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr_merged,
        time_spent=seconds(hours=1)
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr_merged,
        time_spent=seconds(hours=5)
    )

    summary = spent_time_service.get_summary(
        SpentTime.objects.all(),
    )

    assert summary.issues.spent == 0

    assert summary.merge_requests.opened_spent == seconds(hours=5)
    assert summary.merge_requests.closed_spent == seconds(hours=3)
    assert summary.merge_requests.merged_spent == seconds(hours=6)
    assert summary.merge_requests.spent == seconds(hours=14)

    assert summary.spent == seconds(hours=14)
    assert summary.opened_spent == seconds(hours=5)


def test_complex_spents(user):
    IssueSpentTimeFactory.create(
        user=user,
        base=IssueFactory.create(user=user, state=ISSUE_STATES.opened),
        time_spent=seconds(hours=5)
    )

    IssueSpentTimeFactory.create(
        user=user,
        base=IssueFactory.create(user=user, state=ISSUE_STATES.closed),
        time_spent=seconds(hours=3)
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=MergeRequestFactory.create(user=user,
                                        state=MERGE_REQUESTS_STATES.opened),
        time_spent=seconds(hours=5)
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=MergeRequestFactory.create(user=user,
                                        state=MERGE_REQUESTS_STATES.closed),
        time_spent=seconds(hours=3)
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=MergeRequestFactory.create(user=user,
                                        state=MERGE_REQUESTS_STATES.merged),
        time_spent=seconds(hours=6)
    )

    summary = spent_time_service.get_summary(
        SpentTime.objects.all(),
    )

    assert summary.issues.opened_spent == seconds(hours=5)
    assert summary.issues.closed_spent == seconds(hours=3)
    assert summary.issues.spent == seconds(hours=8)

    assert summary.merge_requests.opened_spent == seconds(hours=5)
    assert summary.merge_requests.closed_spent == seconds(hours=3)
    assert summary.merge_requests.merged_spent == seconds(hours=6)
    assert summary.merge_requests.spent == seconds(hours=14)

    assert summary.spent == seconds(hours=22)
    assert summary.opened_spent == seconds(hours=10)


def test_resolver(user, client):
    IssueSpentTimeFactory.create(
        user=user,
        base=IssueFactory.create(user=user, state=ISSUE_STATES.opened),
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=IssueFactory.create(user=user, state=ISSUE_STATES.closed),
        time_spent=seconds(hours=1)
    )

    client.user = user
    info = AttrDict({'context': client})

    summary = resolve_spent_times_summary(
        parent=None,
        info=info,
        state=ISSUE_STATES.opened
    )

    assert summary.merge_requests.spent == 0

    assert summary.issues.opened_spent == seconds(hours=2)
    assert summary.issues.closed_spent == seconds(hours=0)
    assert summary.issues.spent == seconds(hours=2)

    assert summary.spent == seconds(hours=2)
    assert summary.opened_spent == seconds(hours=2)
