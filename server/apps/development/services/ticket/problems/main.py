# -*- coding: utf-8 -*-

from typing import List

from django.db import models

from apps.development.models.ticket import Ticket
from apps.development.services.ticket.problems import checkers

ticket_problem_checkers = [
    checker_class() for checker_class in (checkers.OverDueDateChecker,)
]


def get_ticket_problems(ticket: Ticket) -> List[str]:
    """Get problems for ticket."""
    problems = []

    for checker in ticket_problem_checkers:
        if checker.ticket_has_problem(ticket):
            problems.append(checker.problem_code)

    return problems


def annotate_ticket_problems(queryset: models.QuerySet) -> models.QuerySet:
    """Annotate ticket problems."""
    for checker in ticket_problem_checkers:
        queryset = checker.setup_queryset(queryset)

    return queryset
