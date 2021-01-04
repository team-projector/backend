import django_filters
import graphene
from django.db.models import QuerySet

from apps.core.graphql.fields import BaseModelConnectionField
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

    def filter(  # noqa: A003, WPS125
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering."""
        if not value:
            return queryset

        check_allowed_filtering_by_team(value, self.parent.request.user)

        return queryset.filter(user__teams=value)


class SalaryFilterSet(django_filters.FilterSet):
    """Set of filters for Salary."""

    class Meta:
        model = Salary
        fields = "__all__"

    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    team = TeamFilter()


class AllSalariesConnectionField(BaseModelConnectionField):
    """Handler for workbreaks collections."""

    filterset_class = SalaryFilterSet
    auth_required = True

    def __init__(self):
        """Initialize."""
        super().__init__(
            "apps.payroll.graphql.types.SalaryType",
            user=graphene.ID(),
            team=graphene.ID(),
        )
