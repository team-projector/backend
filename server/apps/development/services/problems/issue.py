# -*- coding: utf-8 -*-

from functools import reduce
from operator import or_, and_
from typing import ClassVar, List

from django.db.models import Case, NullBooleanField, Q, QuerySet, When
from django.utils.timezone import localdate

from apps.development.models.issue import Issue, ISSUE_STATES

PROBLEM_EMPTY_DUE_DAY = 'empty_due_date'
PROBLEM_OVER_DUE_DAY = 'over_due_date'
PROBLEM_EMPTY_ESTIMATE = 'empty_estimate'


class BaseProblemChecker:
    annotate_field: ClassVar[str] = ''
    problem_code: ClassVar[str] = ''

    def setup_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.annotate(**{
            self.annotate_field: Case(
                self.get_condition(),
                output_field=NullBooleanField(),
            ),
        })

    def issue_has_problem(self, issue: Issue) -> bool:
        raise NotImplementedError

    def get_condition(self) -> When:
        raise NotImplementedError


class EmptyDueDateChecker(BaseProblemChecker):
    annotate_field = 'problem_empty_due_date'
    problem_code = PROBLEM_EMPTY_DUE_DAY

    def get_condition(self) -> When:
        return When(
            Q(due_date__isnull=True, state=ISSUE_STATES.opened),
            then=True,
        )

    def issue_has_problem(self, issue: Issue) -> bool:
        return (
            not issue.due_date
            and issue.state == ISSUE_STATES.opened
        )


class OverdueDueDateChecker(BaseProblemChecker):
    annotate_field = 'problem_over_due_date'
    problem_code = PROBLEM_OVER_DUE_DAY

    def get_condition(self) -> When:
        return When(
            Q(due_date__lt=localdate(), state=ISSUE_STATES.opened),
            then=True,
        )

    def issue_has_problem(self, issue: Issue) -> bool:
        return (
            issue.due_date
            and issue.due_date < localdate()
            and issue.state == ISSUE_STATES.opened
        )


class EmptyEstimateChecker(BaseProblemChecker):
    annotate_field = 'problem_empty_estimate'
    problem_code = PROBLEM_EMPTY_ESTIMATE

    def get_condition(self) -> When:
        return When(
            Q(
                Q(time_estimate__isnull=True)
                | Q(time_estimate=0),
            )
            & Q(state=ISSUE_STATES.opened),
            then=True,
        )

    def issue_has_problem(self, issue: Issue) -> bool:
        return (
            not issue.time_estimate
            and issue.state == ISSUE_STATES.opened
        )


checkers = [
    checker_class()
    for checker_class in BaseProblemChecker.__subclasses__()
]


def get_issue_problems(issue: Issue) -> List[str]:
    problems = []

    for checker in checkers:
        if checker.issue_has_problem(issue):
            problems.append(checker.problem_code)

    return problems


def annotate_issues_problems(queryset: QuerySet) -> QuerySet:
    for checker in checkers:
        queryset = checker.setup_queryset(queryset)

    return queryset


def extract_problems_from_annotated(issue: Issue) -> List[str]:
    return [
        checker.problem_code
        for checker in checkers
        if getattr(issue, checker.annotate_field, False)  # noqa WPS425
    ]


def filter_issues_problems(queryset: QuerySet) -> QuerySet:
    return queryset.filter(reduce(or_, [
        Q(**{checker.annotate_field: True})
        for checker in checkers
    ]))


def exclude_issues_problems(queryset: QuerySet) -> QuerySet:
    return queryset.filter(reduce(and_, [
        Q(**{checker.annotate_field: None})
        for checker in checkers
    ]))
