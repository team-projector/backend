from datetime import datetime, timedelta

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from apps.development.services.milestone.problems import (
    PROBLEM_OVER_DUE_DAY,
    get_milestone_problems,
)
from tests.test_development.factories import ProjectMilestoneFactory


@scenario(
    "milestones/problems.feature",
    "Active milestone overdue",
)
def test_active_milestone_overdue():
    """Entry point for "Active milestone overdue" scenario."""


@scenario(
    "milestones/problems.feature",
    "Closed milestone overdue",
)
def test_closed_milestone_overdue():
    """Entry point for "Closed milestone overdue" scenario."""


@pytest.fixture()
def milestone_problems():
    """Captured milestone problems."""
    return []


@given(
    parsers.parse(
        "There is {state} milestone with due date at {days_ago:d} days ago",
    ),
    target_fixture="milestone",
)
def milestone(db, state: str, days_ago: int):
    """Provide active overdued milestone."""
    return ProjectMilestoneFactory.create(
        state=state.upper(),
        due_date=datetime.now().date() - timedelta(days=days_ago),
    )


@when("Check milestone problems")
def check_milestone_problems(milestone, milestone_problems):
    """Check milestones problems."""
    milestone_problems.extend(get_milestone_problems(milestone))


@then("Problem due date overdue should be returned")
def problem_overdue(milestone_problems):
    """Check if overdue problem."""
    assert milestone_problems == [PROBLEM_OVER_DUE_DAY]


@then("No problems")
def no_problems(milestone_problems):
    """Check if no problems."""
    assert not milestone_problems
