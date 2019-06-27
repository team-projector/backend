from typing import ClassVar, Optional

from django.db.models import Case, NullBooleanField, Q, QuerySet, When
from django.utils import timezone

from apps.development.models.issue import STATE_OPENED

PROBLEM_EMPTY_DUE_DAY = 'empty_due_date'
PROBLEM_OVER_DUE_DAY = 'over_due_date'
PROBLEM_EMPTY_ESTIMATE = 'empty_estimate'


class BaseProblemChecker:
    annotate_field: ClassVar[Optional[str]] = None
    problem_code: ClassVar[Optional[str]] = None

    def setup_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.annotate(**{
            self.annotate_field: Case(
                self.get_condition(),
                output_field=NullBooleanField(),
            )
        })

    def get_condition(self) -> When:
        raise NotImplementedError


class EmptyDueDateProblemChecker(BaseProblemChecker):
    annotate_field = 'problem_empty_due_date'
    problem_code = PROBLEM_EMPTY_DUE_DAY

    def get_condition(self) -> When:
        return When(
            Q(due_date__isnull=True, state=STATE_OPENED),
            then=True
        )


class OverdueDueDateProblemChecker(BaseProblemChecker):
    annotate_field = 'problem_over_due_date'
    problem_code = PROBLEM_OVER_DUE_DAY

    def get_condition(self) -> When:
        return When(
            Q(due_date__lt=timezone.now(), state=STATE_OPENED),
            then=True
        )


class EmptyEstimateProblemChecker(BaseProblemChecker):
    annotate_field = 'problem_empty_estimate'
    problem_code = PROBLEM_EMPTY_ESTIMATE

    def get_condition(self) -> When:
        return When(time_estimate__isnull=True, then=True)


checkers = [
    checker_class()
    for checker_class in BaseProblemChecker.__subclasses__()
]


class IssueProblemsChecker:
    def check(self, queryset: QuerySet) -> QuerySet:
        queryset = self._annotate_queryset(queryset)

        return queryset

    @staticmethod
    def _annotate_queryset(queryset: QuerySet) -> QuerySet:
        for checker in checkers:
            queryset = checker.setup_queryset(queryset)

        return queryset
