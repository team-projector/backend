from functools import reduce
from operator import or_

from django.db.models import Case, NullBooleanField, Q, When
from django.utils import timezone

PROBLEM_EMPTY_DUE_DAY = 'empty_due_date'
PROBLEM_OVERDUE_DUE_DAY = 'overdue_due_date'
PROBLEM_EMPTY_ESTIMATE = 'empty_estimate'


class BaseProblemChecker:
    annotate_field = None
    problem_code = None

    def setup_queryset(self, queryset):
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
        return When(due_date__isnull=True, then=True)


class OverdueDueDateProblemChecker(BaseProblemChecker):
    annotate_field = 'problem_overdue_due_date'
    problem_code = PROBLEM_OVERDUE_DUE_DAY

    def get_condition(self) -> When:
        return When(due_date__lt=timezone.now(), then=True)


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
    def check(self, queryset):
        queryset = self._annotate_queryset(queryset)
        queryset = self._filter_queryset(queryset)

        return queryset

    @staticmethod
    def _filter_queryset(queryset):
        return queryset.filter(reduce(or_, [
            Q(**{checker.annotate_field: True})
            for checker in checkers
        ]))

    @staticmethod
    def _annotate_queryset(queryset):
        for checker in checkers:
            queryset = checker.setup_queryset(queryset)

        return queryset
