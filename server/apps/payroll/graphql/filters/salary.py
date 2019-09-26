# -*- coding: utf-8 -*-

import django_filters
from django.db.models import QuerySet

from apps.development.models import Team
from apps.payroll.services.allowed.salary import (
    check_allowed_filtering_by_team,
)
from apps.users.models import User


class TeamFilter(django_filters.ModelChoiceFilter):
    def __init__(self) -> None:
        super().__init__(queryset=Team.objects.all())

    def filter(self, queryset, value) -> QuerySet:
        if not value:
            return queryset

        check_allowed_filtering_by_team(value, self.parent.request.user)

        return queryset.filter(user__teams=value)


class SalaryFilterSet(django_filters.FilterSet):
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    team = TeamFilter()
