import django_filters
import graphene
from django.db.models import QuerySet

from apps.development.models import Team
from apps.payroll.graphql.fields.base import (
    BaseWorkBreaksConnectionField,
    WorkBreakFilterSet,
)
from apps.payroll.services.work_break.allowed import (
    check_allow_filtering_by_team,
)
from apps.users.models import User


class TeamFilter(django_filters.ModelChoiceFilter):
    """Filter work breaks by team."""

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

        check_allow_filtering_by_team(value, self.parent.request.user)

        return queryset.filter(user__teams=value)


class AllWorkBreakFilterSet(WorkBreakFilterSet):
    """Set of filters for Work Break."""

    team = TeamFilter()
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())


class AllWorkBreaksConnectionField(BaseWorkBreaksConnectionField):
    """Handler for workbreaks collections."""

    filterset_class = AllWorkBreakFilterSet

    def __init__(self):
        """Initialize."""
        super().__init__(
            user=graphene.ID(),
            team=graphene.ID(),
        )
