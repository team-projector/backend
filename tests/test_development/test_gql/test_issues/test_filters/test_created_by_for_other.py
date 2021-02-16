from apps.development.graphql.fields.issues import IssuesFilterSet
from apps.development.models.issue import Issue
from tests.test_development.factories import IssueFactory

CREATED_BY_FOR_OTHER = "created_by_for_other"


def test_success(user):
    """Test success query."""
    issue = IssueFactory.create(author=user)
    IssueFactory.create_batch(2, user=user)

    filter_set = IssuesFilterSet(
        data={CREATED_BY_FOR_OTHER: user.pk},
        queryset=Issue.objects.all(),
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 1
    assert filter_set.qs.first() == issue


def test_empty(user):
    """Test empty result."""
    IssueFactory.create(author=user, user=user)
    IssueFactory.create_batch(2, user=user)

    filter_set = IssuesFilterSet(
        data={CREATED_BY_FOR_OTHER: user.pk},
        queryset=Issue.objects.all(),
    )

    assert filter_set.is_valid()
    assert not filter_set.qs.exists()

    assert Issue.objects.filter(author=user).exists()


def test_all_another_issues(user):
    """Test filter by author empty."""
    IssueFactory.create_batch(3)

    filter_set = IssuesFilterSet(
        data={CREATED_BY_FOR_OTHER: user.pk},
        queryset=Issue.objects.all(),
    )

    assert filter_set.is_valid()
    assert not filter_set.qs.exists()


def test_user_as_participant(user):
    """Test user as participiant."""
    issues = IssueFactory.create_batch(3)
    for issue in issues:
        issue.participants.add(user)

    filter_set = IssuesFilterSet(
        data={CREATED_BY_FOR_OTHER: user.pk},
        queryset=Issue.objects.all(),
    )

    assert filter_set.is_valid()
    assert not filter_set.qs.exists()
