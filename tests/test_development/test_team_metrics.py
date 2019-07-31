from datetime import timedelta, datetime

from apps.development.models.issue import STATE_OPENED, STATE_CLOSED
from apps.development.services.metrics.team import get_team_metrics
from tests.test_development.factories import TeamFactory, IssueFactory
from tests.test_users.factories import UserFactory


def test_metrics(user):
    user_1 = UserFactory.create()
    user_2 = UserFactory.create()

    team = TeamFactory.create()
    team.members.set([user, user_1, user_2])

    IssueFactory.create(
        user=user_1,
        due_date=None,
        state=STATE_OPENED,
        title='issue_problem_1'
    )
    IssueFactory.create(
        user=user_1,
        due_date=datetime.now() - timedelta(days=3),
        state=STATE_OPENED,
        title='issue_problem_2'
    )

    IssueFactory.create(
        user=user_1,
        time_estimate=None,
        title='issue_problem_3'
    )

    IssueFactory.create_batch(
        size=4,
        user=user_2,
        due_date=datetime.now() + timedelta(days=3),
        time_estimate=1000,
        state=STATE_CLOSED
    )

    IssueFactory.create_batch(size=5)

    metrics = get_team_metrics(team)

    assert metrics.issues_count == 7
    assert metrics.problems_count == 3
