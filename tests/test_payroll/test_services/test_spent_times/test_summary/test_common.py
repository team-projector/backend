# -*- coding: utf-8 -*-

from apps.core.utils.time import seconds
from apps.development.models.issue import IssueState
from apps.development.models.merge_request import MergeRequestState
from apps.payroll.models import SpentTime
from apps.payroll.services import spent_time as spent_time_service
from tests.test_development.factories import IssueFactory, MergeRequestFactory
from tests.test_payroll.factories import (
    IssueSpentTimeFactory,
    MergeRequestSpentTimeFactory,
)
from tests.test_payroll.test_services.test_spent_times.test_summary import (
    checkers,
)


def test_without_spents(user):
    IssueFactory.create_batch(
        5, user=user, state=IssueState.OPENED, total_time_spent=1000,
    )
    MergeRequestFactory.create_batch(
        5, user=user, state=MergeRequestState.OPENED, total_time_spent=1000,
    )

    summary = spent_time_service.get_summary(SpentTime.objects.all())

    checkers.check_time_spent_summary(summary)
    checkers.check_time_spent_issues_summary(summary.issues)
    checkers.check_time_spent_merge_requests_summary(summary.merge_requests)


def test_issues_spents(user):
    issue_opened = IssueFactory.create(user=user)

    IssueSpentTimeFactory.create(
        user=user, base=issue_opened, time_spent=seconds(hours=2),
    )

    IssueSpentTimeFactory.create(
        user=user, base=issue_opened, time_spent=seconds(hours=3),
    )

    issue_closed = IssueFactory.create(user=user, state=IssueState.CLOSED)

    IssueSpentTimeFactory.create(
        user=user, base=issue_closed, time_spent=seconds(hours=2),
    )

    IssueSpentTimeFactory.create(
        user=user, base=issue_closed, time_spent=seconds(hours=1),
    )

    summary = spent_time_service.get_summary(SpentTime.objects.all())

    checkers.check_time_spent_summary(
        summary,
        spent=seconds(hours=8),
        opened_spent=seconds(hours=5),
        closed_spent=seconds(hours=3),
    )
    checkers.check_time_spent_issues_summary(
        summary.issues,
        opened_spent=seconds(hours=5),
        closed_spent=seconds(hours=3),
        spent=seconds(hours=8),
    )
    checkers.check_time_spent_merge_requests_summary(summary.merge_requests)


def test_merge_requests_spents(user):
    mr_opened = MergeRequestFactory.create(user=user)

    MergeRequestSpentTimeFactory.create(
        user=user, base=mr_opened, time_spent=seconds(hours=2),
    )

    MergeRequestSpentTimeFactory.create(
        user=user, base=mr_opened, time_spent=seconds(hours=3),
    )

    mr_closed = MergeRequestFactory.create(
        user=user, state=MergeRequestState.CLOSED,
    )

    MergeRequestSpentTimeFactory.create(
        user=user, base=mr_closed, time_spent=seconds(hours=2),
    )

    MergeRequestSpentTimeFactory.create(
        user=user, base=mr_closed, time_spent=seconds(hours=1),
    )

    mr_merged = MergeRequestFactory.create(
        user=user, state=MergeRequestState.MERGED,
    )

    MergeRequestSpentTimeFactory.create(
        user=user, base=mr_merged, time_spent=seconds(hours=1),
    )

    MergeRequestSpentTimeFactory.create(
        user=user, base=mr_merged, time_spent=seconds(hours=5),
    )

    summary = spent_time_service.get_summary(SpentTime.objects.all())

    checkers.check_time_spent_summary(
        summary,
        spent=seconds(hours=14),
        opened_spent=seconds(hours=5),
        closed_spent=seconds(hours=9),
    )
    checkers.check_time_spent_issues_summary(summary.issues)
    checkers.check_time_spent_merge_requests_summary(
        summary.merge_requests,
        opened_spent=seconds(hours=5),
        closed_spent=seconds(hours=3),
        merged_spent=seconds(hours=6),
        spent=seconds(hours=14),
    )


def test_complex_spents(user):
    IssueSpentTimeFactory.create(
        user=user,
        base=IssueFactory.create(user=user),
        time_spent=seconds(hours=5),
    )

    IssueSpentTimeFactory.create(
        user=user,
        base=IssueFactory.create(user=user, state=IssueState.CLOSED),
        time_spent=seconds(hours=3),
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=MergeRequestFactory.create(user=user),
        time_spent=seconds(hours=5),
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=MergeRequestFactory.create(
            user=user, state=MergeRequestState.CLOSED,
        ),
        time_spent=seconds(hours=3),
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=MergeRequestFactory.create(
            user=user, state=MergeRequestState.MERGED,
        ),
        time_spent=seconds(hours=6),
    )

    summary = spent_time_service.get_summary(SpentTime.objects.all())

    checkers.check_time_spent_summary(
        summary,
        spent=seconds(hours=22),
        opened_spent=seconds(hours=10),
        closed_spent=seconds(hours=12),
    )
    checkers.check_time_spent_issues_summary(
        summary.issues,
        opened_spent=seconds(hours=5),
        closed_spent=seconds(hours=3),
        spent=seconds(hours=8),
    )
    checkers.check_time_spent_merge_requests_summary(
        summary.merge_requests,
        opened_spent=seconds(hours=5),
        closed_spent=seconds(hours=3),
        merged_spent=seconds(hours=6),
        spent=seconds(hours=14),
    )
