# -*- coding: utf-8 -*-

from typing import ClassVar, List

from django.db.models import Q

from apps.development.models import MergeRequest
from apps.development.models.merge_request import MERGE_REQUESTS_STATES

PROBLEM_EMPTY_ESTIMATE = 'empty_estimate'
PROBLEM_NOT_ASSIGNED = 'not_assigned'


class BaseProblemChecker:
    """A base class checks problems."""

    problem_code: ClassVar[str] = ''

    def merge_request_has_problem(self, merge_request: MergeRequest) -> bool:
        """Method should be implemented in subclass."""
        raise NotImplementedError


class EmptyEstimateChecker(BaseProblemChecker):
    """Check merge request estimate."""

    problem_code = PROBLEM_EMPTY_ESTIMATE

    def merge_request_has_problem(self, merge_request: MergeRequest) -> bool:
        """Current merge request has problem."""
        return merge_request.issues.filter(
            Q(
                Q(time_estimate__isnull=True)
                | Q(time_estimate=0),
            )
            & Q(state=MERGE_REQUESTS_STATES.opened),
        ).exists()


class NotAssignedChecker(BaseProblemChecker):
    """Check merge request not assigned."""

    problem_code = PROBLEM_NOT_ASSIGNED

    def merge_request_has_problem(self, merge_request: MergeRequest) -> bool:
        """Current merge request has problem."""
        return (
            not merge_request.user
            and self._is_done_opened_issues_exists(merge_request)
        )

    def _is_done_opened_issues_exists(
        self,
        merge_request: MergeRequest,
    ) -> bool:
        return merge_request.issues.filter(
            labels__title__iexact='done',
            state=MERGE_REQUESTS_STATES.opened,
        ).exists()


checkers = [
    checker_class()
    for checker_class in (EmptyEstimateChecker, NotAssignedChecker)
]


def get_merge_request_problems(merge_request: MergeRequest) -> List[str]:
    problems = []

    for checker in checkers:
        if checker.merge_request_has_problem(merge_request):
            problems.append(checker.problem_code)

    return problems
