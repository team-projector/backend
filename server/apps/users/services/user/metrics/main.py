# -*- coding: utf-8 -*-

from django.db.models import Q, Sum
from django.db.models.functions import Coalesce

from apps.development.models import MergeRequest
from apps.development.models.issue import ISSUE_STATES, Issue
from apps.development.models.merge_request import MERGE_REQUESTS_STATES
from apps.payroll.models import Bonus, Penalty, SpentTime
from apps.users.models import User


class WorkItemUserMetrics:
    """Work item user metrics uses for issues or merge requests."""

    opened_count: int = 0
    closed_spent: float = 0
    opened_spent: float = 0


class IssueUserMetrics(WorkItemUserMetrics):
    """Issue user metrics."""

    def __init__(self, user: User):
        """Calculate and return user issues metrics."""
        self.opened_count = self._get_issues_opened_count(user)
        self.closed_spent = self._get_issues_closed_spent(user)
        self.opened_spent = self._get_issues_opened_spent(user)

    def _get_issues_opened_count(self, user: User) -> int:
        return Issue.objects.filter(
            user=user,
            state=ISSUE_STATES.OPENED,
        ).count()

    def _get_issues_closed_spent(self, user: User) -> float:
        return SpentTime.objects.filter(
            salary__isnull=True,
            user=user,
            issues__state=ISSUE_STATES.CLOSED,
        ).aggregate(
            total_time_spent=Coalesce(Sum('time_spent'), 0),
        )['total_time_spent']

    def _get_issues_opened_spent(self, user: User) -> float:
        return SpentTime.objects.filter(
            salary__isnull=True,
            user=user,
            issues__state=ISSUE_STATES.OPENED,
        ).aggregate(
            total_time_spent=Coalesce(Sum('time_spent'), 0),
        )['total_time_spent']


class MergeRequestUserMetrics(WorkItemUserMetrics):
    """Merge Request user metrics."""

    def __init__(self, user: User):
        """Calculate and return user merge requests metrics."""
        self.opened_count = self._get_merge_requests_opened_count(user)
        self.closed_spent = self._get_merge_requests_closed_spent(user)
        self.opened_spent = self._get_merge_requests_opened_spent(user)

    def _get_merge_requests_opened_count(self, user: User) -> int:
        return MergeRequest.objects.filter(
            user=user,
            state=ISSUE_STATES.OPENED,
        ).count()

    def _get_merge_requests_closed_spent(self, user: User) -> float:
        return SpentTime.objects.filter(
            salary__isnull=True,
            user=user,
            mergerequests__state__in=(
                MERGE_REQUESTS_STATES.CLOSED,
                MERGE_REQUESTS_STATES.MERGED,
            ),
        ).aggregate(
            total_time_spent=Coalesce(Sum('time_spent'), 0),
        )['total_time_spent']

    def _get_merge_requests_opened_spent(self, user: User) -> float:
        return SpentTime.objects.filter(
            salary__isnull=True,
            user=user,
            mergerequests__state=ISSUE_STATES.OPENED,
        ).aggregate(
            total_time_spent=Coalesce(Sum('time_spent'), 0),
        )['total_time_spent']


class UserMetrics:
    """User metrics fields."""

    payroll_closed: float = 0
    payroll_opened: float = 0
    bonus: float = 0
    penalty: float = 0
    issues: IssueUserMetrics
    merge_requests: MergeRequestUserMetrics


class UserMetricsProvider:
    """User metrics provider."""

    def get_metrics(self, user: User) -> UserMetrics:
        """Calculate and return metrics."""
        metrics = UserMetrics()

        metrics.bonus = self._get_bonus(user)
        metrics.penalty = self._get_penalty(user)
        metrics.payroll_opened = self._get_payroll_opened(user)
        metrics.payroll_closed = self._get_payroll_closed(user)

        metrics.issues = IssueUserMetrics(user)
        metrics.merge_requests = MergeRequestUserMetrics(user)

        return metrics

    def _get_bonus(self, user: User) -> float:
        return Bonus.objects.filter(
            user=user,
            salary__isnull=True,
        ).aggregate(
            total_bonus=Coalesce(Sum('sum'), 0),
        )['total_bonus']

    def _get_penalty(self, user: User) -> float:
        return Penalty.objects.filter(
            user=user,
            salary__isnull=True,
        ).aggregate(
            total_penalty=Coalesce(Sum('sum'), 0),
        )['total_penalty']

    def _get_payroll_opened(self, user: User) -> float:
        return SpentTime.objects.filter(
            Q(issues__state=ISSUE_STATES.OPENED)
            | Q(mergerequests__state=ISSUE_STATES.OPENED),
            salary__isnull=True,
            user=user,
        ).aggregate(
            total_sum=Coalesce(Sum('sum'), 0),
        )['total_sum']

    def _get_payroll_closed(self, user: User) -> float:
        return SpentTime.objects.filter(
            Q(issues__state=ISSUE_STATES.CLOSED)
            | Q(mergerequests__state__in=(
                MERGE_REQUESTS_STATES.CLOSED,
                MERGE_REQUESTS_STATES.MERGED,
            )),
            salary__isnull=True,
            user=user,
        ).aggregate(
            total_sum=Coalesce(Sum('sum'), 0),
        )['total_sum']
