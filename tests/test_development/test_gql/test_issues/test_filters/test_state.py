from apps.development.graphql.fields.issues import IssuesFilterSet
from apps.development.models.issue import Issue, IssueState
from tests.test_development.factories import IssueFactory


def test_opened(user):
    """Test filter by opened state."""
    issue = IssueFactory.create(user=user, state=IssueState.OPENED)
    IssueFactory.create_batch(5, user=user, state="")

    queryset = IssuesFilterSet(
        data={"state": IssueState.OPENED},
        queryset=Issue.objects.all(),
    ).qs

    assert queryset.count() == 1
    assert queryset.first() == issue


def test_closed(user):
    """Test filter by closed state."""
    IssueFactory.create_batch(5, user=user, state="")
    issue = IssueFactory.create(user=user, state=IssueState.CLOSED)

    queryset = IssuesFilterSet(
        data={"state": IssueState.CLOSED},
        queryset=Issue.objects.all(),
    ).qs

    assert queryset.count() == 1
    assert queryset.first() == issue
