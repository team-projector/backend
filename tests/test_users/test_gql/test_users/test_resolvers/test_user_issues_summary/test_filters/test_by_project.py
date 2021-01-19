from apps.development.models.issue import Issue
from apps.users.graphql.resolvers.user_issues_summary import (
    UserIssuesSummaryFilterSet,
)
from tests.test_development.factories import IssueFactory


def test_filter_by_project(user, project):
    """Test filter by project."""
    issue = IssueFactory.create(project=project)
    IssueFactory.create_batch(3)

    issues = UserIssuesSummaryFilterSet(
        data={"project": project.pk},
        queryset=Issue.objects.all(),
    ).qs

    assert Issue.objects.count() == 4
    assert issues.count() == 1
    assert issues.first() == issue


def test_filter_by_project_empty(user, project):
    """Test filter by project empty."""
    IssueFactory.create_batch(3)

    issues = UserIssuesSummaryFilterSet(
        data={"project": project.pk},
        queryset=Issue.objects.all(),
    ).qs

    assert Issue.objects.count() == 3
    assert not issues.exists()
