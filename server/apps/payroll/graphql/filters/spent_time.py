# -*- coding: utf-8 -*-

import django_filters
from django.db.models import QuerySet

from apps.core.graphql.filters.ordering import OrderingFilter
from apps.development.models import Project, Team, TeamMember
from apps.payroll.models import Salary, SpentTime
from apps.users.models import User


class TeamFilter(django_filters.ModelChoiceFilter):
    """Filter spent times by team."""

    def __init__(self) -> None:
        """Initialize self."""
        super().__init__(queryset=Team.objects.all())

    def filter(self, queryset, value) -> QuerySet:  # noqa: A003, WPS110
        """Do filtering."""
        if not value:
            return queryset

        users = TeamMember.objects.get_no_watchers(value)
        return queryset.filter(user__in=users)


class ProjectFilter(django_filters.ModelChoiceFilter):
    """Filter spent times by project."""

    def __init__(self) -> None:
        """Initialize self."""
        super().__init__(queryset=Project.objects.all())

    def filter(self, queryset, value) -> QuerySet:  # noqa: A003, WPS110
        """Do filtering."""
        if not value:
            return queryset

        return queryset.filter(issues__project=value) | queryset.filter(
            mergerequests__project=value,
        )


class StateFilter(django_filters.CharFilter):
    """Filter spent times by state."""

    def filter(self, queryset, value) -> QuerySet:  # noqa: A003, WPS110
        """Do filtering."""
        if not value or value == "all":
            return queryset

        return queryset.filter(issues__state=value) | queryset.filter(
            mergerequests__state=value,
        )


class SpentTimeFilterSet(django_filters.FilterSet):
    """Set of filters for Spent Time."""

    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    project = ProjectFilter()
    team = TeamFilter()
    state = StateFilter()
    salary = django_filters.ModelChoiceFilter(queryset=Salary.objects.all())

    order_by = OrderingFilter(fields=("date", "created_at"))

    class Meta:
        model = SpentTime
        fields = ("date", "user", "salary", "team", "state")
