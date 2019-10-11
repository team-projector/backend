# -*- coding: utf-8 -*-

import django_filters
from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from apps.core.graphql.filters import SearchFilter
from apps.core.graphql.filters.ordering import OrderingFilter

from ...models import Issue, Milestone, Project, Team, TeamMember, Ticket
from ...services import issue as issue_service

User = get_user_model()


class TicketFilter(django_filters.ModelChoiceFilter):
    """Filter issues by ticket."""

    def __init__(self) -> None:
        """
        Initialize self.

        Set queryset.
        """
        super().__init__(queryset=Ticket.objects.all())

    def filter(self, queryset, value) -> QuerySet:  # noqa A003
        """Do filtering."""
        if not value:
            return queryset

        issue_service.check_allow_project_manager(self.parent.request.user)

        return queryset.filter(ticket=value)


class MilestoneFilter(django_filters.ModelChoiceFilter):
    """Filter issues by milestone."""

    def __init__(self) -> None:
        """Initialize self."""
        super().__init__(queryset=Milestone.objects.all())

    def filter(self, queryset, value) -> QuerySet:  # noqa A003
        """Do filtering."""
        if not value:
            return queryset

        issue_service.check_allow_project_manager(self.parent.request.user)

        return queryset.filter(milestone=value)


class ProblemsFilter(django_filters.BooleanFilter):
    """Filter issues by problem."""

    def filter(self, queryset, value) -> QuerySet:  # noqa A003
        """Do filtering."""
        if value is None:
            return queryset

        queryset = issue_service.annotate_problems(queryset)

        if value is True:
            queryset = issue_service.filter_problems(queryset)
        elif value is False:
            queryset = issue_service.exclude_problems(queryset)

        return queryset


class TeamFilter(django_filters.ModelChoiceFilter):
    """Filter issues by team."""

    def __init__(self) -> None:
        """Initialize self."""
        super().__init__(queryset=Team.objects.all())

    def filter(self, queryset, value) -> QuerySet:  # noqa A003
        """Do filtering."""
        if not value:
            return queryset

        users = TeamMember.objects.get_no_watchers(value)
        return queryset.filter(user__in=users)


class IssuesFilterSet(django_filters.FilterSet):
    """Set of filters for Issues."""

    milestone = MilestoneFilter()
    problems = ProblemsFilter()
    project = django_filters.ModelChoiceFilter(queryset=Project.objects.all())
    team = TeamFilter()
    ticket = TicketFilter()
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())

    order_by = OrderingFilter(
        fields=('due_date', 'title', 'created_at', 'closed_at'),
    )

    q = SearchFilter(fields=('title',))  # noqa WPS111

    class Meta:
        model = Issue
        fields = (
            'state', 'due_date', 'user', 'team', 'problems', 'project',
            'milestone', 'ticket',
        )
