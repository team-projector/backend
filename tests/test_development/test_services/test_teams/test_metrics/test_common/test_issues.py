from datetime import datetime, timedelta

from apps.core.utils.time import seconds
from apps.development.graphql.types.team import TeamType
from apps.development.models import Team
from apps.development.models.issue import IssueState
from apps.development.services.team.metrics.main import get_team_metrics
from tests.test_development.factories import IssueFactory
from tests.test_development.test_services.test_teams.test_metrics.test_common.checker import (  # noqa: E501
    check_team_metrics,
)


def test_basic(team: Team):
    IssueFactory.create_batch(
        2,
        user=team.members.all()[0],
        due_date=datetime.now() + timedelta(days=1),
        time_estimate=seconds(hours=2),
        state=IssueState.OPENED
    )
    IssueFactory.create_batch(
        4,
        user=team.members.all()[1],
        due_date=datetime.now() + timedelta(days=2),
        time_estimate=seconds(hours=3),
        state=IssueState.CLOSED
    )

    IssueFactory.create_batch(size=5)

    check_team_metrics(
        get_team_metrics(team),
        issues_count=6,
        issues_opened_count=2,
        issues_opened_estimated=seconds(hours=4)
    )


def test_problems(team: Team):
    IssueFactory.create(
        user=team.members.all()[0],
        due_date=None,
        state=IssueState.OPENED,
        time_estimate=seconds(hours=1),
        title="issue_problem_1"
    )
    IssueFactory.create(
        user=team.members.all()[0],
        due_date=datetime.now() - timedelta(days=3),
        time_estimate=seconds(hours=3),
        state=IssueState.OPENED,
        title="issue_problem_2"
    )
    IssueFactory.create(
        user=team.members.all()[0],
        time_estimate=None,
        title="issue_problem_3",
        state=IssueState.OPENED
    )
    IssueFactory.create_batch(
        size=4,
        user=team.members.all()[1],
        due_date=datetime.now() + timedelta(days=3),
        time_estimate=seconds(hours=3),
        state=IssueState.CLOSED
    )

    IssueFactory.create_batch(size=5)

    check_team_metrics(
        get_team_metrics(team),
        problems_count=3,
        issues_count=7,
        issues_opened_count=3,
        issues_opened_estimated=seconds(hours=4),
    )


def test_resolver(team: Team):
    IssueFactory.create_batch(
        2,
        user=team.members.all()[0],
        due_date=datetime.now() + timedelta(days=1),
        time_estimate=seconds(hours=2),
        state=IssueState.OPENED
    )

    check_team_metrics(
        TeamType.resolve_metrics(team, None),
        issues_count=2,
        issues_opened_count=2,
        issues_opened_estimated=seconds(hours=4),
    )
