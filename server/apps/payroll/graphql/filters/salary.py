# -*- coding: utf-8 -*-

import django_filters
from django.db.models import QuerySet

from apps.development.models import Team
from apps.payroll.models import Salary
from apps.payroll.services.salary.allowed import (
    check_allowed_filtering_by_team,
)
from apps.users.models import User


class TeamFilter(django_filters.ModelChoiceFilter):
    """Filter salaries by team."""

    def __init__(self) -> None:
        """Initialize self."""
        super().__init__(queryset=Team.objects.all())

    def filter(self, queryset, value) -> QuerySet:  # noqa: WPS125, WPS110
        """Do filtering."""
        if not value:
            return queryset

        check_allowed_filtering_by_team(value, self.parent.request.user)

        return queryset.filter(user__teams=value)


class SalaryFilterSet(django_filters.FilterSet):
    """Set of filters for Salary."""

    class Meta:
        model = Salary
        fields = ("user", "team")

    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    team = TeamFilter()
