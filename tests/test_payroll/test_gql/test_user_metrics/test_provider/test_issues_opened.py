from apps.development.models.issue import IssueState
from apps.users.logic.services.user.metrics.resolvers import (
    opened_issues_count_resolver,
)
from tests.test_development.factories import IssueFactory
from tests.test_users.factories.user import UserFactory


def test_issues_opened_count(user, ghl_auth_mock_info):
    """
    Test issues opened count.

    :param user:
    :param ghl_auth_mock_info:
    """
    IssueFactory.create_batch(5, user=user)

    expected = opened_issues_count_resolver(user)
    assert expected == 5


def test_issues_opened_count_another_user(user, ghl_auth_mock_info):
    """
    Test issues opened count another user.

    :param user:
    :param ghl_auth_mock_info:
    """
    IssueFactory.create_batch(2, user=user)
    IssueFactory.create_batch(5, user=UserFactory.create())

    expected = opened_issues_count_resolver(user)
    assert expected == 2


def test_issues_opened_count_exists_closed(user, ghl_auth_mock_info):
    """
    Test issues opened count exists closed.

    :param user:
    :param ghl_auth_mock_info:
    """
    IssueFactory.create_batch(5, user=user)
    IssueFactory.create_batch(5, user=user, state=IssueState.CLOSED)

    expected = opened_issues_count_resolver(user)
    assert expected == 5
