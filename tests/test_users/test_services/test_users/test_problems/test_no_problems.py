from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.users.services.user.problems import get_user_problems
from tests.test_development.factories import IssueFactory


def test_no_problems(user):
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

    assert not get_user_problems(user)
