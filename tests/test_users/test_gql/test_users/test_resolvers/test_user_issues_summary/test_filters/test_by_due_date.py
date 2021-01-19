from datetime import datetime, timedelta

from apps.development.models.issue import Issue
from apps.users.graphql.resolvers.user_issues_summary import (
    UserIssuesSummaryFilterSet,
)
from tests.test_development.factories import IssueFactory


def test_filter_by_due_date(user):
    """Test filter by due_date."""
    now = datetime.now().date()
    tomorrow = now + timedelta(days=1)

    issue = IssueFactory.create(due_date=tomorrow)
    IssueFactory.create_batch(3, due_date=now)

    issues = UserIssuesSummaryFilterSet(
        data={"due_date": tomorrow},
        queryset=Issue.objects.all(),
    ).qs

    assert Issue.objects.count() == 4
    assert issues.count() == 1
    assert issues.first() == issue


def test_filter_by_due_date_empty(user, ghl_auth_mock_info):
    """Test filter by due_date empty."""
    now = datetime.now().date()

    IssueFactory.create_batch(2, due_date=now)

    issues = UserIssuesSummaryFilterSet(
        data={"due_date": now + timedelta(days=2)},
        queryset=Issue.objects.all(),
    ).qs

    assert Issue.objects.count() == 2
    assert not issues.exists()
