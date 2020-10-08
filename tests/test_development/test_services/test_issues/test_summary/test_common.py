from datetime import datetime

from apps.development.models.issue import Issue, IssueState
from apps.development.services.issue.summary import get_issues_summary
from tests.test_development.factories import IssueFactory
from tests.test_development.test_services.test_issues.test_summary.helpers import (  # noqa: E501
    checkers,
)
from tests.test_users.factories.user import UserFactory


def test_counts(user):
    """
    Test counts.

    :param user:
    """
    IssueFactory.create_batch(
        5,
        user=user,
        state=IssueState.OPENED,
        total_time_spent=0,
        due_date=datetime.now(),
    )
    IssueFactory.create_batch(
        3,
        user=user,
        state=IssueState.CLOSED,
        total_time_spent=0,
        due_date=datetime.now(),
    )

    summary = get_issues_summary(Issue.objects.filter(user=user), user=user)

    checkers.check_summary(summary, count=8, opened_count=5, closed_count=3)


def test_problems(user):
    """
    Test problems.

    :param user:
    """
    IssueFactory.create_batch(4, user=user, total_time_spent=0)
    IssueFactory.create(
        user=user,
        total_time_spent=0,
        due_date=datetime.now(),
    )
    IssueFactory.create_batch(2, user=UserFactory.create(), total_time_spent=0)

    summary = get_issues_summary(Issue.objects.filter(user=user), user=user)

    checkers.check_summary(summary, count=5, opened_count=5, problems_count=4)
