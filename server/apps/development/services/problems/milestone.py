from typing import ClassVar, List

from django.db.models import Case, NullBooleanField, Q, QuerySet, When
from django.utils.timezone import localdate

from apps.development.models import Milestone

PROBLEM_OVER_DUE_DAY = 'over_due_date'


class BaseProblemChecker:
    annotate_field: ClassVar[str] = ''
    problem_code: ClassVar[str] = ''

    def setup_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.annotate(**{
            self.annotate_field: Case(
                self.get_condition(),
                output_field=NullBooleanField(),
            )
        })

    def milestone_has_problem(self, milestone: Milestone) -> bool:
        raise NotImplementedError

    def get_condition(self) -> When:
        raise NotImplementedError


class OverdueDueDateChecker(BaseProblemChecker):
    annotate_field = 'problem_over_due_date'
    problem_code = PROBLEM_OVER_DUE_DAY

    def get_condition(self) -> When:
        return When(
            Q(due_date__lt=localdate(), state=Milestone.STATE.active),
            then=True
        )

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
