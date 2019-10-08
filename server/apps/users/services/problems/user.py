# -*- coding: utf-8 -*-

from typing import Iterable

from apps.users.models import User
from apps.users.services.problems.checkers import PayrollOpenedOverflowChecker

checkers = [
    checker_class()
    for checker_class in (PayrollOpenedOverflowChecker,)
]


def get_user_problems(user: User) -> Iterable[str]:
    """Get problems for user."""
    problems = []

    for checker in checkers:
        problem = checker.check(user)
        if problem:
            problems.append(problem)

    return problems
