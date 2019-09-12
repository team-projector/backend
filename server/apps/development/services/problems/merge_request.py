from typing import ClassVar, List
from django.db.models import Q

from apps.development.models.issue import STATE_OPENED
from apps.development.models import MergeRequest

PROBLEM_EMPTY_ESTIMATE = 'empty_estimate'
PROBLEM_NOT_ASSIGNED = 'not_assigned'


class BaseProblemChecker:
    problem_code: ClassVar[str] = ''

    def merge_request_has_problem(self, merge_request: MergeRequest) -> bool:
        raise NotImplementedError


class EmptyEstimateChecker(BaseProblemChecker):
    problem_code = PROBLEM_EMPTY_ESTIMATE

    def merge_request_has_problem(self, merge_request: MergeRequest) -> bool:
        return merge_request.issues.filter(
            Q(
                Q(time_estimate__isnull=True) |
                Q(time_estimate=0)
            ) &
            Q(state=STATE_OPENED)
        ).exists()


class NotAssignedChecker(BaseProblemChecker):
    problem_code = PROBLEM_NOT_ASSIGNED

    def merge_request_has_problem(self, merge_request: MergeRequest) -> bool:
        return (
            not merge_request.user
            and merge_request.issues.filter(labels__title='Done').exists()
        )


checkers = [
    checker_class()
    for checker_class in BaseProblemChecker.__subclasses__()
]


def get_merge_request_problems(merge_request: MergeRequest) -> List[str]:
    problems = []

    for checker in checkers:
        if checker.merge_request_has_problem(merge_request):
            problems.append(checker.problem_code)

    return problems
