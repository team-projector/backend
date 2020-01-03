# -*- coding: utf-8 -*-

from typing import ClassVar, List

from django.utils.timezone import localdate

from apps.development.models import Milestone
from apps.development.models.milestone import MILESTONE_STATES

PROBLEM_OVER_DUE_DAY = "OVER_DUE_DATE"


class BaseProblemChecker:
    """A base class checks problems."""

    problem_code: ClassVar[str] = ""

    def milestone_has_problem(self, milestone: Milestone) -> bool:
        """Method should be implemented in subclass."""
        raise NotImplementedError


class OverdueDueDateChecker(BaseProblemChecker):
    """Check milestone overdue due date."""

    problem_code = PROBLEM_OVER_DUE_DAY

    def milestone_has_problem(self, milestone: Milestone) -> bool:
        """Current milestone has problem condition."""
        return (
            milestone.due_date
            and milestone.due_date < localdate()
            and milestone.state == MILESTONE_STATES.ACTIVE
        )


checkers = [
    checker_class()
    for checker_class in (OverdueDueDateChecker,)
]


def get_milestone_problems(milestone: Milestone) -> List[str]:
    """Get problems for milestone."""
    problems = []

    for checker in checkers:
        if checker.milestone_has_problem(milestone):
            problems.append(checker.problem_code)

    return problems
