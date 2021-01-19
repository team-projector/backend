from apps.development.graphql.fields.issues import IssuesFilterSet
from apps.development.models.issue import Issue
from tests.test_development.factories import IssueFactory


def test_by_assignee(user):
    """Test by assignee."""
    issues = IssueFactory.create_batch(2, user=user)
    IssueFactory.create_batch(2)

    filter_set = IssuesFilterSet(
        data={"assigned_to": user.pk},
        queryset=Issue.objects.all(),
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 2
    assert set(filter_set.qs) == set(issues)


def test_filter_by_assignee_empty(user):
    """Test filter by assignee empty."""
    IssueFactory.create_batch(2, author=user)

    filter_set = IssuesFilterSet(
        data={"assigned_to": user.pk},
        queryset=Issue.objects.all(),
    )

    assert filter_set.is_valid()
    assert not filter_set.qs.exists()
