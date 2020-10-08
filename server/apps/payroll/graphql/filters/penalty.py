import django_filters

from apps.payroll.graphql.filters.team import TeamFilter
from apps.payroll.models import Penalty, Salary
from apps.users.models import User


class PenaltyFilterSet(django_filters.FilterSet):
    """Set of filters for Penalty."""

    class Meta:
        model = Penalty
        fields = ("user", "salary", "team")

    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    salary = django_filters.ModelChoiceFilter(queryset=Salary.objects.all())
    team = TeamFilter()
