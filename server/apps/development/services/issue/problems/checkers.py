# -*- coding: utf-8 -*-

from typing import ClassVar

from django.db import models
from django.db.models import Case, NullBooleanField, QuerySet, When
from django.utils.timezone import localdate

from apps.development.models.issue import ISSUE_STATES, Issue

PROBLEM_EMPTY_DUE_DAY = 'EMPTY_DUE_DATE'
PROBLEM_OVER_DUE_DAY = 'OVER_DUE_DATE'
PROBLEM_EMPTY_ESTIMATE = 'EMPTY_ESTIMATE'


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
            models.Q(due_date__isnull=True, state=ISSUE_STATES.OPENED),
            then=True,
        )

    def issue_has_problem(self, issue: Issue) -> bool:
        """Current issue has problem."""
        return (
            not issue.due_date
            and issue.state == ISSUE_STATES.OPENED
        )


class OverdueDueDateChecker(BaseProblemChecker):
    """Check issue overdue due date."""

    annotate_field = 'problem_over_due_date'
    problem_code = PROBLEM_OVER_DUE_DAY

    def get_condition(self) -> When:
        """Get condition."""
        return When(
            models.Q(due_date__lt=localdate(), state=ISSUE_STATES.OPENED),
            then=True,
        )

    def issue_has_problem(self, issue: Issue) -> bool:
        """Current issue has problem."""
        return (
            issue.due_date
            and issue.due_date < localdate()
            and issue.state == ISSUE_STATES.OPENED
        )


class EmptyEstimateChecker(BaseProblemChecker):
    """Check issue empty estimate."""

    annotate_field = 'problem_empty_estimate'
    problem_code = PROBLEM_EMPTY_ESTIMATE

    def get_condition(self) -> When:
        """Get condition."""
        return When(
            models.Q(
                models.Q(time_estimate__isnull=True)
                | models.Q(time_estimate=0),
            )
            & models.Q(state=ISSUE_STATES.OPENED),
            then=True,
        )

    def issue_has_problem(self, issue: Issue) -> bool:
        """Current issue has problem."""
        return (
            not issue.time_estimate
            and issue.state == ISSUE_STATES.OPENED
        )
