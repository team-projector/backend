from typing import List

import pytest

from apps.development.models.issue import Issue, IssueState
from tests.test_development.factories import IssueFactory
from tests.test_users.factories import UserFactory


@pytest.fixture()
def issues_created_by(user) -> List[Issue]:
    """Create issues with author=user."""
    total = 6
    opened = 3

    issues = []
    for issue_number in range(total):
        issue = IssueFactory.create(
            author=user,
            state=IssueState.OPENED
            if issue_number < opened
            else IssueState.CLOSED,
            user=UserFactory.create(),
        )
        _add_participants(issue)
        issues.append(issue)

    return issues


@pytest.fixture()
def issues_assigned(user) -> List[Issue]:
    """Create issues with assigned=user."""
    total = 3
    opened = 1

    issues = []
    for issue_number in range(total):
        issue = IssueFactory.create(
            user=user,
            state=IssueState.OPENED
            if issue_number < opened
            else IssueState.CLOSED,
            author=UserFactory.create(),
        )
        _add_participants(issue)
        issues.append(issue)

    return issues


@pytest.fixture()
def issues_participation(user) -> List[Issue]:
    """Create issues with participation=user."""
    total = 4
    opened = 0

    issues = []
    for issue_number in range(total):
        issue = IssueFactory.create(
            user=UserFactory.create(),
            state=IssueState.OPENED
            if issue_number < opened
            else IssueState.CLOSED,
            author=UserFactory.create(),
        )
        _add_participants(issue, user)
        issues.append(issue)

    return issues


def _add_participants(issue, user1=None, user2=None) -> None:
    """Add participants to issue."""
    issue.participants.add(
        user1 or UserFactory.create(),
        user2 or UserFactory.create(),
    )
