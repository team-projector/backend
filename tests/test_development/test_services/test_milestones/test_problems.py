from datetime import datetime, timedelta

from apps.development.models.milestone import MilestoneState
from apps.development.services.milestone.problems import (
    PROBLEM_OVER_DUE_DAY,
    get_milestone_problems,
)
from tests.test_development.factories import ProjectMilestoneFactory


def test_overdue_due_day(db):
    """
    Test overdue due day.

    :param db:
    """
    problem_milestone = ProjectMilestoneFactory.create(
        state=MilestoneState.ACTIVE,
        due_date=datetime.now().date() - timedelta(days=1),
    )

    assert get_milestone_problems(problem_milestone) == [PROBLEM_OVER_DUE_DAY]


def test_overdue_due_day_but_closed(db):
    """
    Test overdue due day but closed.

    :param db:
    """
    milestone = ProjectMilestoneFactory.create(
        state=MilestoneState.CLOSED,
        due_date=datetime.now().date() - timedelta(days=1),
    )

    assert not get_milestone_problems(milestone)
