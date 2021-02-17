from apps.development.models.issue import Issue, IssueState
from apps.users.models import User
from apps.users.services.user.summary.provider import UserIssuesSummary


def assert_user_issue_summary(
    user: User,
    issues_summary: UserIssuesSummary,
) -> None:
    """Assert user issue summary."""
    _assert_assigned(
        user,
        issues_summary.assigned_count,
        issues_summary.assigned_opened_count,
    )
    _assert_created(
        user,
        issues_summary.created_count,
        issues_summary.created_opened_count,
    )
    _assert_participations(
        user,
        issues_summary.participation_count,
        issues_summary.participation_opened_count,
    )
    _assert_created_by_for_other(
        user,
        issues_summary.created_by_for_other_count,
        issues_summary.created_by_for_other_opened_count,
    )


def _assert_assigned(user, total, opened) -> None:
    """Assert assignee."""
    issues = Issue.objects.filter(user=user)
    assert issues.count() == total
    assert issues.filter(state=IssueState.OPENED).count() == opened


def _assert_created(user, total, opened) -> None:
    """Assert created by."""
    issues = Issue.objects.filter(author=user)
    assert issues.count() == total
    assert issues.filter(state=IssueState.OPENED).count() == opened


def _assert_created_by_for_other(user, total, opened) -> None:
    """Assert created_by_for_other."""
    issues = Issue.objects.filter(author=user).exclude(user=user)
    assert issues.count() == total
    assert issues.filter(state=IssueState.OPENED).count() == opened


def _assert_participations(user, total, opened) -> None:
    """Assert participations."""
    issues = Issue.objects.filter(participants=user)
    assert issues.count() == total
    assert issues.filter(state=IssueState.OPENED).count() == opened
