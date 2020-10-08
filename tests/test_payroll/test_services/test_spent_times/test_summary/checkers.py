from apps.payroll.services.spent_time.summary import (
    IssuesSpentTimesSummary,
    MergeRequestsSpentTimesSummary,
    SpentTimesSummary,
)


def check_time_spent_summary(
    summary: SpentTimesSummary,
    spent: int = 0,
    opened_spent: int = 0,
    closed_spent: int = 0,
):
    """Check time spent summary."""
    assert summary.spent == spent
    assert summary.opened_spent == opened_spent
    assert summary.closed_spent == closed_spent


def check_time_spent_issues_summary(
    summary: IssuesSpentTimesSummary,
    spent: int = 0,
    opened_spent: int = 0,
    closed_spent: int = 0,
):
    """Check time spent issues summary."""
    assert summary.spent == spent
    assert summary.opened_spent == opened_spent
    assert summary.closed_spent == closed_spent


def check_time_spent_merge_requests_summary(
    summary: MergeRequestsSpentTimesSummary,
    spent: int = 0,
    opened_spent: int = 0,
    closed_spent: int = 0,
    merged_spent: int = 0,
):
    """Check time spent merge requests summary."""
    assert summary.spent == spent
    assert summary.opened_spent == opened_spent
    assert summary.closed_spent == closed_spent
    assert summary.merged_spent == merged_spent
