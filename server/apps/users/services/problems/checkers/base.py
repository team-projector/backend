from typing import ClassVar, Optional

from apps.users.models import User


class BaseProblemChecker:
    problem_code: ClassVar[Optional[str]] = None

    def check(self, user: User) -> Optional[str]:
        if self.has_problem(user):
            return self.problem_code

    def has_problem(self, user: User) -> bool:
        raise NotImplementedError
