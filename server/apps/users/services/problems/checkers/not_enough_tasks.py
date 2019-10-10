# -*- coding: utf-8 -*-

from django.db.models import F, Sum

from apps.core.consts import SECONDS_PER_HOUR
from apps.development.models.issue import ISSUE_STATES, Issue
from apps.development.models.merge_request import (
    MERGE_REQUESTS_STATES,
    MergeRequest,
)
from apps.users.models import User
from apps.users.services.problems.checkers import BaseProblemChecker

PROBLEM_NOT_ENOUGH_TASKS = 'not_enough_tasks'


class NotEnoughTasksChecker(BaseProblemChecker):
    """A class indicates a problem that user has not enough tasks."""

    problem_code = PROBLEM_NOT_ENOUGH_TASKS

    def has_problem(self, user: User) -> bool:
        """
        User has problem.

        If user's daily work hours more than difference between
        estimate and total user's time spent.
        """
        issues = Issue.objects.filter(
            user=user,
            state=ISSUE_STATES.opened,
        )
        merge_requests = MergeRequest.objects.filter(
            user=user,
            state=MERGE_REQUESTS_STATES.opened,
        )

        if not issues and not merge_requests:
            return False

        issues_time_remains = self._aggregate_time_remains(issues)
        mrs_time_remains = self._aggregate_time_remains(merge_requests)

        daily_work_hours = user.daily_work_hours * SECONDS_PER_HOUR

        return issues_time_remains + mrs_time_remains < daily_work_hours

    def _aggregate_time_remains(self, queryset) -> int:
        return queryset.annotate(
            time_remains=F('time_estimate') - F('total_time_spent'),
        ).aggregate(
            total_time_remains=Sum('time_remains'),
        )['total_time_remains'] or 0
