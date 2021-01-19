from apps.development.graphql.fields.issues import IssuesFilterSet
from apps.development.models.issue import Issue
from tests.test_development.factories import IssueFactory


def test_by_participant(user):
    """Test by participant."""
    issue = IssueFactory.create(author=user)
    issue.participants.add(user)
    IssueFactory.create_batch(2, user=user)

    filter_set = IssuesFilterSet(
        data={"participated_by": user.pk},
        queryset=Issue.objects.all(),
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 1
    assert filter_set.qs.first() == issue


def test_filter_by_participant_empty(user):
    """Test filter by participant empty."""
    IssueFactory.create_batch(3, user=user)

    filter_set = IssuesFilterSet(
        data={"participated_by": user.pk},
        queryset=Issue.objects.all(),
    )

    assert filter_set.is_valid()
    assert not filter_set.qs.exists()
