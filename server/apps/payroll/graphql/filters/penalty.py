# -*- coding: utf-8 -*-

import django_filters

from apps.payroll.models import Salary
from apps.users.models import User


class PenaltyFilterSet(django_filters.FilterSet):
    """Set of filters for Penalty."""

    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    salary = django_filters.ModelChoiceFilter(queryset=Salary.objects.all())
