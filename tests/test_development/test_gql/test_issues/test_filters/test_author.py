from apps.development.graphql.fields.issues import IssuesFilterSet
from apps.development.models.issue import Issue
from tests.test_development.factories import IssueFactory


def test_by_author(user):
    """Test by author."""
    issue = IssueFactory.create(author=user)
    IssueFactory.create_batch(2, user=user)

    filter_set = IssuesFilterSet(
        data={"created_by": user.pk},
        queryset=Issue.objects.all(),
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 1
    assert filter_set.qs.first() == issue


def test_filter_by_author_empty(user):
    """Test filter by author empty."""
    IssueFactory.create_batch(3, user=user)

    filter_set = IssuesFilterSet(
        data={"created_by": user.pk},
        queryset=Issue.objects.all(),
    )

    assert filter_set.is_valid()
    assert not filter_set.qs.exists()
