# -*- coding: utf-8 -*-

from functools import reduce
from operator import and_, or_
from typing import List

from django.db.models import Q, QuerySet

from apps.development.models.issue import Issue
from apps.development.services.issue.problems import checkers

issue_problem_checkers = [
    checker_class()
    for checker_class in (
        checkers.EmptyDueDateChecker,
        checkers.OverdueDueDateChecker,
        checkers.EmptyEstimateChecker,
    )
]


def get_problems(issue: Issue) -> List[str]:
    """Get problems for issue."""
    problems = []

    for checker in issue_problem_checkers:
        if checker.issue_has_problem(issue):
            problems.append(checker.problem_code)

    return problems


def annotate_problems(queryset: QuerySet) -> QuerySet:
    """Annotate issues problems."""
    for checker in issue_problem_checkers:
        queryset = checker.setup_queryset(queryset)

    return queryset


def filter_problems(queryset: QuerySet) -> QuerySet:
    """Get problems from issues."""
    return queryset.filter(reduce(or_, [
        Q(**{checker.annotate_field: True})
        for checker in issue_problem_checkers
    ]))


def exclude_problems(queryset: QuerySet) -> QuerySet:
    """Exclude problems from issues."""
    return queryset.filter(reduce(and_, [
        Q(**{checker.annotate_field: None})
        for checker in issue_problem_checkers
    ]))