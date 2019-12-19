# -*- coding: utf-8 -*-

from typing import ClassVar, List

from django.db import models

from apps.development.models import MergeRequest
from apps.development.models.merge_request import MERGE_REQUESTS_STATES

PROBLEM_EMPTY_ESTIMATE = 'EMPTY_ESTIMATE'
PROBLEM_NOT_ASSIGNED = 'NOT_ASSIGNED'


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
            models.Q(
                models.Q(time_estimate__isnull=True)
                | models.Q(time_estimate=0),
            )
            & models.Q(state=MERGE_REQUESTS_STATES.OPENED),
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
            state=MERGE_REQUESTS_STATES.OPENED,
        ).exists()


checkers = [
    checker_class()
    for checker_class in (EmptyEstimateChecker, NotAssignedChecker)
]


def get_merge_request_problems(merge_request: MergeRequest) -> List[str]:
    """Get problems for merge request."""
    problems = []

    for checker in checkers:
        if checker.merge_request_has_problem(merge_request):
            problems.append(checker.problem_code)

    return problems
