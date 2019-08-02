from datetime import timedelta, datetime

from apps.development.models import MergeRequest
from apps.development.models.issue import STATE_OPENED, STATE_CLOSED
from apps.development.services.metrics.team import get_team_metrics
from tests.test_development.factories import (
    IssueFactory, MergeRequestFactory, TeamFactory
)
from tests.test_users.factories import UserFactory


def test_issues_problems(user):
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
        title='issue_problem_3',
        state=STATE_OPENED
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

    assert metrics.issues.count == 7
    assert metrics.problems_count == 3


def test_issues(user):
    user_1 = UserFactory.create()
    user_2 = UserFactory.create()

    team = TeamFactory.create()
    team.members.set([user, user_1, user_2])

    IssueFactory.create_batch(
        2,
        user=user_1,
        due_date=datetime.now() + timedelta(days=1),
        time_estimate=360,
        state=STATE_OPENED
    )
    IssueFactory.create_batch(
        size=4,
        user=user_2,
        due_date=datetime.now() + timedelta(days=2),
        time_estimate=1000,
        state=STATE_CLOSED
    )

    IssueFactory.create_batch(size=5)

    metrics = get_team_metrics(team)

    assert metrics.problems_count == 0
    assert metrics.merge_requests.count == 0

    assert metrics.issues.count == 6
    assert metrics.issues.opened_count == 2
    assert metrics.issues.opened_estimated == 720


def test_merge_requests(user):
    user_1 = UserFactory.create()
    user_2 = UserFactory.create()

    team = TeamFactory.create()
    team.members.set([user, user_1, user_2])

    MergeRequestFactory.create_batch(
        2,
        user=user_1,
        time_estimate=360,
        state=MergeRequest.STATE.opened
    )
    MergeRequestFactory.create_batch(
        3,
        user=user_1,
        time_estimate=1000,
        state=MergeRequest.STATE.closed
    )
    MergeRequestFactory.create_batch(
        3,
        user=user_2,
        time_estimate=1500,
        state=MergeRequest.STATE.closed
    )

    MergeRequestFactory.create_batch(size=5)

    metrics = get_team_metrics(team)

    assert metrics.issues.count == 0

    assert metrics.merge_requests.count == 8
    assert metrics.merge_requests.opened_count == 2
    assert metrics.merge_requests.opened_estimated == 720

