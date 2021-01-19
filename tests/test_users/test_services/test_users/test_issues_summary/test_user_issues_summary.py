from apps.development.models import Issue
from apps.users.services.user.summary.issues import get_user_issues_summary
from tests.test_development.factories import IssueFactory


def test_get_issues_summary(user, ghl_auth_mock_info):
    """Test user issues summary."""
    IssueFactory.create_batch(2, author=user)
    IssueFactory.create_batch(2, author=user, user=user)
    issues = IssueFactory.create_batch(3)

    for issue in issues:
        issue.participants.add(user)

    issues[0].user = user
    issues[0].save()

    issues_summary = get_user_issues_summary(user)

    assert Issue.objects.count() == 7
    assert issues_summary.assigned_count == 3
    assert issues_summary.created_count == 4
    assert issues_summary.participation_count == 3


def test_get_issues_summary_empty(user, ghl_auth_mock_info):
    """Test user issues summary empty."""
    IssueFactory.create_batch(2)

    issues_summary = get_user_issues_summary(user)

    assert Issue.objects.count() == 2
    assert not issues_summary.assigned_count
    assert not issues_summary.created_count
    assert not issues_summary.participation_count
