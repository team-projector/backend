import django_filters
import graphene
from django.db.models import QuerySet

from apps.core.graphql.fields import BaseModelConnectionField
from apps.core.graphql.queries.filters import OrderingFilter
from apps.development.models import Project, Team, TeamMember
from apps.payroll.models import Salary, SpentTime
from apps.users.models import User


class TeamFilter(django_filters.ModelChoiceFilter):
    """Filter spent times by team."""

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

        users = TeamMember.objects.get_no_watchers(value)
        return queryset.filter(user__in=users)


class ProjectFilter(django_filters.ModelChoiceFilter):
    """Filter spent times by project."""

    def __init__(self) -> None:
        """Initialize self."""
        super().__init__(queryset=Project.objects.all())

    def filter(  # noqa: A003, WPS125
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering."""
        if not value:
            return queryset

        return queryset.filter(issues__project=value) | queryset.filter(
            mergerequests__project=value,
        )


class StateFilter(django_filters.CharFilter):
    """Filter spent times by state."""

    def filter(  # noqa: A003, WPS125
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering."""
        if not value or value == "all":
            return queryset

        return queryset.filter(issues__state=value) | queryset.filter(
            mergerequests__state=value,
        )


class SpentTimeFilterSet(django_filters.FilterSet):
    """Set of filters for Spent Time."""

    class Meta:
        model = SpentTime
        fields = "__all__"

    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    salary = django_filters.ModelChoiceFilter(queryset=Salary.objects.all())
    team = TeamFilter()
    project = ProjectFilter()
    state = StateFilter()
    order_by = OrderingFilter(fields=("date", "created_at"))


class AllSpentTimesConnectionField(BaseModelConnectionField):
    """Handler for all spent time collections."""

    filterset_class = SpentTimeFilterSet

    def __init__(self):
        """Initialize."""
        super().__init__(
            "payroll.SpentTimeType",
            user=graphene.ID(),
            project=graphene.ID(),
            team=graphene.ID(),
            state=graphene.String(),
            salary=graphene.ID(),
            order_by=graphene.String(),
        )
