from typing import ClassVar, List

from django.utils.timezone import localdate

from apps.development.models import Milestone

PROBLEM_OVER_DUE_DAY = 'over_due_date'


class BaseProblemChecker:
    problem_code: ClassVar[str] = ''

    def milestone_has_problem(self, milestone: Milestone) -> bool:
        raise NotImplementedError


class OverdueDueDateChecker(BaseProblemChecker):
    problem_code = PROBLEM_OVER_DUE_DAY

    def milestone_has_problem(self, milestone: Milestone) -> bool:
        return (milestone.due_date and
                milestone.due_date < localdate() and
                milestone.state == Milestone.STATE.active)


checkers = [
    checker_class()
    for checker_class in BaseProblemChecker.__subclasses__()
]


def get_milestone_problems(milestone: Milestone) -> List[str]:
    problems = []

    for checker in checkers:
        if checker.milestone_has_problem(milestone):
            problems.append(checker.problem_code)

    return problems
