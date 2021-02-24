from datetime import datetime, timedelta

from apps.development.graphql.fields.issues import IssuesFilterSet
from apps.development.models.issue import Issue
from tests.test_development.factories import IssueFactory


def test_by_due_date(user):
    """
    Test by due date.

    :param user:
    """
    issue = IssueFactory.create(user=user, due_date=datetime.now())
    IssueFactory.create(
        user=user,
        due_date=datetime.now() + timedelta(days=1),
    )
    IssueFactory.create(
        user=user,
        due_date=datetime.now() - timedelta(days=1),
    )

    issues = IssuesFilterSet(
        data={"due_date": datetime.now().date()},
        queryset=Issue.objects.all(),
    ).qs

    assert issues.count() == 1
    assert issues.first() == issue
