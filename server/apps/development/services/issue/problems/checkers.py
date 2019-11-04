# -*- coding: utf-8 -*-

from typing import ClassVar

from django.db.models import Case, NullBooleanField, Q, QuerySet, When
from django.utils.timezone import localdate

from apps.development.models.issue import ISSUE_STATES, Issue

PROBLEM_EMPTY_DUE_DAY = 'empty_due_date'
PROBLEM_OVER_DUE_DAY = 'over_due_date'
PROBLEM_EMPTY_ESTIMATE = 'empty_estimate'


class BaseProblemChecker:
    """A base class checks issue problems."""

    annotate_field: ClassVar[str] = ''
    problem_code: ClassVar[str] = ''

    def setup_queryset(self, queryset: QuerySet) -> QuerySet:
        """Setup queryset."""
        return queryset.annotate(**{
            self.annotate_field: Case(
                self.get_condition(),
                output_field=NullBooleanField(),
            ),
        })

    def issue_has_problem(self, issue: Issue) -> bool:
        """Method should be implemented in subclass."""
        raise NotImplementedError

    def get_condition(self) -> When:
        """Method should be implemented in subclass."""
        raise NotImplementedError


class EmptyDueDateChecker(BaseProblemChecker):
    """Check issue empty due date."""

    annotate_field = 'problem_empty_due_date'
    problem_code = PROBLEM_EMPTY_DUE_DAY

    def get_condition(self) -> When:
        """Get condition."""
        return When(
            Q(due_date__isnull=True, state=ISSUE_STATES.opened),
            then=True,
        )

    def issue_has_problem(self, issue: Issue) -> bool:
        """Current issue has problem."""
        return (
            not issue.due_date
            and issue.state == ISSUE_STATES.opened
        )


class OverdueDueDateChecker(BaseProblemChecker):
    """Check issue overdue due date."""

    annotate_field = 'problem_over_due_date'
    problem_code = PROBLEM_OVER_DUE_DAY

    def get_condition(self) -> When:
        """Get condition."""
        return When(
            Q(due_date__lt=localdate(), state=ISSUE_STATES.opened),
            then=True,
        )

    def issue_has_problem(self, issue: Issue) -> bool:
        """Current issue has problem."""
        return (
            issue.due_date
            and issue.due_date < localdate()
            and issue.state == ISSUE_STATES.opened
        )


class EmptyEstimateChecker(BaseProblemChecker):
    """Check issue empty estimate."""

    annotate_field = 'problem_empty_estimate'
    problem_code = PROBLEM_EMPTY_ESTIMATE

    def get_condition(self) -> When:
        """Get condition."""
        return When(
            Q(
                Q(time_estimate__isnull=True)
                | Q(time_estimate=0),
            )
            & Q(state=ISSUE_STATES.opened),
            then=True,
        )

    def issue_has_problem(self, issue: Issue) -> bool:
        """Current issue has problem."""
        return (
            not issue.time_estimate
            and issue.state == ISSUE_STATES.opened
        )