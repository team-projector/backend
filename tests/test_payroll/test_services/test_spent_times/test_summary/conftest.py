import pytest
from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.merge_request import MergeRequestState
from tests.test_development.factories import MergeRequestFactory
from tests.test_payroll.factories import MergeRequestSpentTimeFactory


@pytest.fixture()
def mr_opened(user):
    """Create opened merge request with spents."""
    merge_request = MergeRequestFactory.create(
        user=user,
        state=MergeRequestState.OPENED,
    )

    for opened_spent in (2, 3):
        _add_spend(user, merge_request, opened_spent)

    return merge_request


@pytest.fixture()
def mr_closed(user):
    """Create closed merge request with spents."""
    merge_request = MergeRequestFactory.create(
        user=user,
        state=MergeRequestState.CLOSED,
    )

    for closed_spent in (2, 1):
        _add_spend(user, merge_request, closed_spent)

    return merge_request


@pytest.fixture()
def mr_merged(user):
    """Create merged merge request with spents."""
    merge_request = MergeRequestFactory.create(
        user=user,
        state=MergeRequestState.MERGED,
    )

    for merged_spent in (1, 5):
        _add_spend(user, merge_request, merged_spent)

    return merge_request


def _add_spend(user, base, hours) -> None:
    """Add spent time for merge request."""
    MergeRequestSpentTimeFactory.create(
        user=user,
        base=base,
        time_spent=seconds(hours=hours),
    )
