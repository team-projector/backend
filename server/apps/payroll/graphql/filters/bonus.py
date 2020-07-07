# -*- coding: utf-8 -*-

import django_filters

from apps.payroll.models import Bonus, Salary
from apps.users.models import User


class BonusFilterSet(django_filters.FilterSet):
    """Set of filters for Bonus."""

    class Meta:
        model = Bonus
        fields = ("user", "salary")

    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    salary = django_filters.ModelChoiceFilter(queryset=Salary.objects.all())
