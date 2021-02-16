from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from tests.test_development.factories import IssueFactory


def test_no_problems(user, user_problems_service):
    """Test if user has"t any problem."""
    IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=5),
        total_time_spent=seconds(hours=1),
        state=IssueState.OPENED,
    )

    IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=4),
        total_time_spent=0,
        state=IssueState.OPENED,
    )

    assert not user_problems_service.get_problems(user)
