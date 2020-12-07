from apps.development.models.issue import IssueState
from apps.users.services.user import metrics
from tests.test_development.factories import MergeRequestFactory
from tests.test_users.factories.user import UserFactory


def test_mr_opened_count(user, ghl_auth_mock_info):
    """
    Test mr opened count.

    :param user:
    :param ghl_auth_mock_info:
    """
    MergeRequestFactory.create_batch(5, user=user)

    expected = metrics.mr_opened_count_resolver(None, ghl_auth_mock_info)
    assert expected == 5


def test_mr_opened_count_exists_closed(user, ghl_auth_mock_info):
    """
    Test mr opened count exists closed.

    :param user:
    :param ghl_auth_mock_info:
    """
    MergeRequestFactory.create_batch(2, user=user)
    MergeRequestFactory.create_batch(5, user=user, state=IssueState.CLOSED)

    expected = metrics.mr_opened_count_resolver(None, ghl_auth_mock_info)
    assert expected == 2


def test_mr_opened_count_another_user(user, ghl_auth_mock_info):
    """
    Test mr opened count another user.

    :param user:
    :param ghl_auth_mock_info:
    """
    MergeRequestFactory.create_batch(2, user=user)
    MergeRequestFactory.create_batch(5, user=UserFactory.create())

    expected = metrics.mr_opened_count_resolver(None, ghl_auth_mock_info)
    assert expected == 2
