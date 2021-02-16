from typing import Iterable

from apps.users.logic.services.user.problems import (
    IUserProblemsService,
    checkers,
)
from apps.users.models import User

CHECKERS_CLASSES = (
    checkers.NotEnoughTasksChecker,
    checkers.PayrollOpenedOverflowChecker,
)


class UserProblemsService(IUserProblemsService):
    """Service for checking user problems."""

    def __init__(self):
        """Initializing."""
        self._checkers = [
            checker_class() for checker_class in CHECKERS_CLASSES
        ]

    def get_problems(self, user: User) -> Iterable[str]:
        """Get problems for user."""
        problems = []

        for checker in self._checkers:
            problem = checker.check(user)
            if problem:
                problems.append(problem)

        return problems
