# -*- coding: utf-8 -*-

from typing import Iterable

from apps.users.models import User
from apps.users.services.problems.checkers.base import BaseProblemChecker

checkers = [
    checker_class()
    for checker_class in BaseProblemChecker.__subclasses__()
]


def get_user_problems(user: User) -> Iterable[str]:
    problems = []

    for checker in checkers:
        problem = checker.check(user)
        if problem:
            problems.append(problem)

    return problems
