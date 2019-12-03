from datetime import datetime, timedelta
from pytest import raises

from apps.development.graphql.types.milestone import MilestoneType
from apps.development.models.milestone import MILESTONE_STATES
from apps.development.services.milestone import (
    get_problems, PROBLEM_OVER_DUE_DAY
)
from apps.development.services.milestone.problems import BaseProblemChecker
from tests.test_development.factories import ProjectMilestoneFactory


def test_base_checker():
    with raises(NotImplementedError):
        BaseProblemChecker().milestone_has_problem(None)


def test_overdue_due_day(db):
    problem_milestone = ProjectMilestoneFactory.create(
        state=MILESTONE_STATES.ACTIVE,
        due_date=datetime.now().date() - timedelta(days=1)
    )

    assert get_problems(problem_milestone) == [PROBLEM_OVER_DUE_DAY]


def test_overdue_due_day_but_closed(db):
    milestone = ProjectMilestoneFactory.create(
        state=MILESTONE_STATES.CLOSED,
        due_date=datetime.now().date() - timedelta(days=1)
    )

    assert get_problems(milestone) == []


def test_resolver(db):
    problem_milestone = ProjectMilestoneFactory.create(
        state=MILESTONE_STATES.ACTIVE,
        due_date=datetime.now().date() - timedelta(days=1)
    )

    problems = MilestoneType.resolve_problems(problem_milestone, None)
    assert problems == [PROBLEM_OVER_DUE_DAY]
