# -*- coding: utf-8 -*-

from typing import Iterable

from apps.users.models import User

from .checkers import NotEnoughTasksChecker, PayrollOpenedOverflowChecker

checkers = [
    checker_class()
    for checker_class in (NotEnoughTasksChecker, PayrollOpenedOverflowChecker)
]


def get_problems(user: User) -> Iterable[str]:
    """Get problems for user."""
    problems = []

    for checker in checkers:
        problem = checker.check(user)
        if problem:
            problems.append(problem)

    return problems
