# -*- coding: utf-8 -*-

from typing import ClassVar, Optional

from apps.users.models import User


class BaseProblemChecker:
    """A base class checks problems for user instance."""

    problem_code: ClassVar[Optional[str]] = None

    def check(self, user: User) -> Optional[str]:
        """Handling problem for user."""
        if self.has_problem(user):
            return self.problem_code

    def has_problem(self, user: User) -> bool:
        """Problem condition should be implemented in subclasses."""
        raise NotImplementedError
