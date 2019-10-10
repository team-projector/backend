from datetime import timedelta, datetime

from apps.core.utils.time import seconds
from apps.development.graphql.types.team import TeamType
from apps.development.models.issue import ISSUE_STATES
from apps.development.models.merge_request import MERGE_REQUESTS_STATES
from apps.development.services.team.metrics.main import get_metrics
from tests.test_development.factories import (
    IssueFactory, MergeRequestFactory, TeamFactory
)
from tests.test_users.factories import UserFactory


def test_issues(user):
    user_1 = UserFactory.create()
    user_2 = UserFactory.create()

    team = TeamFactory.create()
    team.members.set([user, user_1, user_2])

    IssueFactory.create_batch(
        2,
        user=user_1,
        due_date=datetime.now() + timedelta(days=1),
        time_estimate=seconds(hours=2),
        state=ISSUE_STATES.opened
    )
    IssueFactory.create_batch(
        size=4,
        user=user_2,
        due_date=datetime.now() + timedelta(days=2),
        time_estimate=seconds(hours=3),
        state=ISSUE_STATES.closed
    )

    IssueFactory.create_batch(size=5)

    metrics = get_metrics(team)

    assert metrics.problems_count == 0
    assert metrics.merge_requests.count == 0

    assert metrics.issues.count == 6
    assert metrics.issues.opened_count == 2
    assert metrics.issues.opened_estimated == seconds(hours=4)


def test_merge_requests(user):
    user_1 = UserFactory.create()
    user_2 = UserFactory.create()

    team = TeamFactory.create()
    team.members.set([user, user_1, user_2])

    MergeRequestFactory.create_batch(
        2,
        user=user_1,
        time_estimate=seconds(hours=2),
        state=MERGE_REQUESTS_STATES.opened
    )
    MergeRequestFactory.create_batch(
        3,
        user=user_1,
        time_estimate=seconds(hours=3),
        state=MERGE_REQUESTS_STATES.closed
    )
    MergeRequestFactory.create_batch(
        3,
        user=user_2,
        time_estimate=seconds(hours=4),
        state=MERGE_REQUESTS_STATES.closed
    )

    MergeRequestFactory.create_batch(size=5)

    metrics = get_metrics(team)

    assert metrics.issues.count == 0

    assert metrics.merge_requests.count == 8
    assert metrics.merge_requests.opened_count == 2
    assert metrics.merge_requests.opened_estimated == seconds(hours=4)


def test_issues_problems(user):
    user_1 = UserFactory.create()
    user_2 = UserFactory.create()

    team = TeamFactory.create()
    team.members.set([user, user_1, user_2])

    IssueFactory.create(
        user=user_1,
        due_date=None,
        state=ISSUE_STATES.opened,
        title='issue_problem_1'
    )
    IssueFactory.create(
        user=user_1,
        due_date=datetime.now() - timedelta(days=3),
        state=ISSUE_STATES.opened,
        title='issue_problem_2'
    )
    IssueFactory.create(
        user=user_1,
        time_estimate=None,
        title='issue_problem_3',
        state=ISSUE_STATES.opened
    )
    IssueFactory.create_batch(
        size=4,
        user=user_2,
        due_date=datetime.now() + timedelta(days=3),
        time_estimate=seconds(hours=3),
        state=ISSUE_STATES.closed
    )

    IssueFactory.create_batch(size=5)

    metrics = get_metrics(team)

    assert metrics.issues.count == 7
    assert metrics.problems_count == 3


def test_resolver(user):
    team = TeamFactory.create()
    team.members.add(user)

    IssueFactory.create_batch(
        2,
        user=user,
        due_date=datetime.now() + timedelta(days=1),
        time_estimate=seconds(hours=2),
        state=ISSUE_STATES.opened
    )

    metrics = TeamType.resolve_metrics(team, None)

    assert metrics.issues.count == 2
    assert metrics.issues.opened_count == 2
    assert metrics.issues.opened_estimated == seconds(hours=4)
