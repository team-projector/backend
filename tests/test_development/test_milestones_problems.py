from datetime import datetime, timedelta

from apps.development.models import Milestone
from apps.development.services.problems.milestone import (
    get_milestone_problems, PROBLEM_OVER_DUE_DAY
)
from tests.test_development.factories import ProjectMilestoneFactory


def test_overdue_due_day(db):
    problem_milestone = ProjectMilestoneFactory.create(
        state=Milestone.STATE.active,
        due_date=datetime.now().date() - timedelta(days=1)
    )

    assert get_milestone_problems(problem_milestone) == [PROBLEM_OVER_DUE_DAY]


def test_overdue_due_day_but_closed(db):
    milestone = ProjectMilestoneFactory.create(
        state=Milestone.STATE.closed,
        due_date=datetime.now().date() - timedelta(days=1)
    )

    assert get_milestone_problems(milestone) == []
