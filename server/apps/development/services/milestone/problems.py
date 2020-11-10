from typing import ClassVar, List

from django.contrib.auth import get_user_model
from django.utils.timezone import localdate
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models import Milestone
from apps.development.models.milestone import MilestoneState
from apps.development.services.milestone.allowed import is_project_manager

PROBLEM_OVER_DUE_DAY = "OVER_DUE_DATE"

User = get_user_model()


class BaseProblemChecker:
    """A base class checks problems."""

    problem_code: ClassVar[str] = ""

    def milestone_has_problem(self, milestone: Milestone) -> bool:
        """Method should be implemented in subclass."""
        raise NotImplementedError


class OverdueDueDateChecker(BaseProblemChecker):
    """Check milestone overdue due date."""

    problem_code = PROBLEM_OVER_DUE_DAY

    def milestone_has_problem(self, milestone: Milestone) -> bool:
        """Current milestone has problem condition."""
        return (
            milestone.due_date
            and milestone.due_date < localdate()
            and milestone.state == MilestoneState.ACTIVE
        )


checkers = [checker_class() for checker_class in (OverdueDueDateChecker,)]


def get_milestone_problems(milestone: Milestone) -> List[str]:
    """Get problems for milestone."""
    problems = []

    for checker in checkers:
        if checker.milestone_has_problem(milestone):
            problems.append(checker.problem_code)

    return problems


def get_milestone_problems_for_user(
    user: User,  # type: ignore
    milestone: Milestone,
) -> List[str]:
    """Get milestone problems for user."""
    if is_project_manager(user, milestone):
        return get_milestone_problems(milestone)

    raise GraphQLPermissionDenied(
        "Only project managers can view project resources",
    )
