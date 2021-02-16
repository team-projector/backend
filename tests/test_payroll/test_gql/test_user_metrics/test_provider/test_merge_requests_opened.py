from apps.development.models.issue import IssueState
from apps.users.logic.services.user.metrics.resolvers import (
    opened_merge_requests_count_resolver,
)
from tests.test_development.factories import MergeRequestFactory
from tests.test_users.factories.user import UserFactory


def test_mr_opened_count(user, ghl_auth_mock_info):
    """
    Test mr opened count.

    :param user:
    :param ghl_auth_mock_info:
    """
    MergeRequestFactory.create_batch(5, user=user)

    metrics = opened_merge_requests_count_resolver(user)
    assert metrics == 5


def test_mr_opened_count_exists_closed(user, ghl_auth_mock_info):
    """
    Test mr opened count exists closed.

    :param user:
    :param ghl_auth_mock_info:
    """
    MergeRequestFactory.create_batch(2, user=user)
    MergeRequestFactory.create_batch(5, user=user, state=IssueState.CLOSED)

    metrics = opened_merge_requests_count_resolver(user)
    assert metrics == 2


def test_mr_opened_count_another_user(user, ghl_auth_mock_info):
    """
    Test mr opened count another user.

    :param user:
    :param ghl_auth_mock_info:
    """
    MergeRequestFactory.create_batch(2, user=user)
    MergeRequestFactory.create_batch(5, user=UserFactory.create())

    metrics = opened_merge_requests_count_resolver(user)
    assert metrics == 2
