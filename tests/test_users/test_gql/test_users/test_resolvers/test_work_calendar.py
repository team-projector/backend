from datetime import datetime

from apps.development.models import Issue
from apps.users.graphql.resolvers import resolve_work_calendar
from tests.test_development.factories import IssueFactory


def test_success(user, ghl_auth_mock_info):
    """Test sucess user metrics resolving."""
    today = datetime.now().date()

    issue = IssueFactory.create(user=user, due_date=today)

    work_calendar = resolve_work_calendar(
        parent=None,
        info=ghl_auth_mock_info,
        user=user.pk,
        start=today,
        end=today,
    )

    assert len(work_calendar) == 1
    first_day = work_calendar[0]
    assert first_day.date == today

    _assert_issues(first_day.issues, Issue.objects.filter(id=issue.id))
    _assert_metrics(first_day.metrics)


def _assert_issues(metrics_issues, issues) -> None:
    """Assert issues."""
    assert metrics_issues.count() == issues.count()
    assert set(metrics_issues.values_list("id", flat=True)) == set(
        issues.values_list("id", flat=True),
    )


def _assert_metrics(metrics) -> None:
    """Assert metrics."""
    assert metrics.start == metrics.end
    assert metrics.issues_count == 1
