from apps.development.models import MergeRequest
from apps.development.services.merge_request.allowed import (
    filter_allowed_for_user,
)
from tests.test_development.factories import MergeRequestFactory
from tests.test_users.factories.user import UserFactory


def test_by_assignee(user):
    """
    Test by assignee.

    :param user:
    """
    MergeRequestFactory.create_batch(4, user=user)
    MergeRequestFactory.create_batch(2, user=UserFactory.create())

    allowed = filter_allowed_for_user(MergeRequest.objects.all(), user)

    assert allowed.count() == 4


def test_by_team_leader(team_leader, team_developer):
    """
    Test by team leader.

    :param team_leader:
    :param team_developer:
    """
    MergeRequestFactory.create_batch(4, user=team_developer)

    allowed = filter_allowed_for_user(MergeRequest.objects.all(), team_leader)

    assert allowed.count() == 4


def test_by_team_leader_and_user(team_leader, team_developer):
    """
    Test by team leader and user.

    :param team_leader:
    :param team_developer:
    """
    MergeRequestFactory.create_batch(4, user=team_developer)
    MergeRequestFactory.create_batch(3, user=team_leader)

    allowed = filter_allowed_for_user(MergeRequest.objects.all(), team_leader)

    assert allowed.count() == 7


def test_by_team_watcher(team_developer, team_watcher):
    """
    Test by team watcher.

    :param team_developer:
    :param team_watcher:
    """
    MergeRequestFactory.create_batch(4, user=team_developer)

    allowed = filter_allowed_for_user(MergeRequest.objects.all(), team_watcher)
    assert allowed.count() == 4
