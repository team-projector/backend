import django_filters
import graphene

from apps.core.graphql.fields import BaseModelConnectionField
from apps.payroll.graphql.filters.team import TeamFilter
from apps.payroll.models import Penalty, Salary
from apps.users.models import User


class PenaltyFilterSet(django_filters.FilterSet):
    """Set of filters for Penalty."""

    class Meta:
        model = Penalty
        fields = "__all__"

    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    salary = django_filters.ModelChoiceFilter(queryset=Salary.objects.all())
    team = TeamFilter()


class AllPenaltiesConnectionField(BaseModelConnectionField):
    """Handler for workbreaks collections."""

    filterset_class = PenaltyFilterSet

    def __init__(self):
        """Initialize."""
        super().__init__(
            "payroll.PenaltyType",
            user=graphene.ID(),
            salary=graphene.ID(),
            team=graphene.ID(),
        )
