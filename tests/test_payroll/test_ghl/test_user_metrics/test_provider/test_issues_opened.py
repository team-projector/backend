from apps.development.models.issue import IssueState
from apps.users.services.user import metrics
from tests.test_development.factories import IssueFactory
from tests.test_users.factories.user import UserFactory


def test_issues_opened_count(user, ghl_auth_mock_info):
    """
    Test issues opened count.

    :param user:
    :param ghl_auth_mock_info:
    """
    IssueFactory.create_batch(5, user=user)

    expected = metrics.issues_opened_count_resolver(None, ghl_auth_mock_info)
    assert expected == 5


def test_issues_opened_count_another_user(user, ghl_auth_mock_info):
    """
    Test issues opened count another user.

    :param user:
    :param ghl_auth_mock_info:
    """
    IssueFactory.create_batch(2, user=user)
    IssueFactory.create_batch(5, user=UserFactory.create())

    expected = metrics.issues_opened_count_resolver(None, ghl_auth_mock_info)
    assert expected == 2


def test_issues_opened_count_exists_closed(user, ghl_auth_mock_info):
    """
    Test issues opened count exists closed.

    :param user:
    :param ghl_auth_mock_info:
    """
    IssueFactory.create_batch(5, user=user)
    IssueFactory.create_batch(5, user=user, state=IssueState.CLOSED)

    expected = metrics.issues_opened_count_resolver(None, ghl_auth_mock_info)
    assert expected == 5
