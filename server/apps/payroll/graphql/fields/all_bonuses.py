import django_filters
import graphene

from apps.core.graphql.fields import BaseModelConnectionField
from apps.payroll.graphql.filters.team import TeamFilter
from apps.payroll.models import Bonus, Salary
from apps.users.models import User


class BonusFilterSet(django_filters.FilterSet):
    """Set of filters for Bonus."""

    class Meta:
        model = Bonus
        fields = "__all__"

    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    salary = django_filters.ModelChoiceFilter(queryset=Salary.objects.all())
    team = TeamFilter()


class AllBonusesConnectionField(BaseModelConnectionField):
    """Handler for workbreaks collections."""

    filterset_class = BonusFilterSet

    def __init__(self):
        """Initialize."""
        super().__init__(
            "payroll.BonusType",
            user=graphene.ID(),
            salary=graphene.ID(),
            team=graphene.ID(),
        )
