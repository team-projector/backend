import django_filters
from django.db.models import Exists, OuterRef, QuerySet
from jnt_django_graphene_toolbox.filters import OrderingFilter

from apps.development.models import Team, TeamMember
from apps.payroll.models import WorkBreak
from apps.payroll.models.mixins.approved import ApprovedState
from apps.payroll.services.work_break.allowed import (
    check_allow_filtering_by_team,
)
from apps.users.models import User


class ApprovingFilter(django_filters.BooleanFilter):
    """Filter work breaks by approved state."""

    def filter(  # noqa: A003, WPS125
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering."""
        if not value:
            return queryset

        teams = TeamMember.objects.filter(
            user=self.parent.request.user,
            roles=TeamMember.roles.LEADER,
        ).values_list("team", flat=True)

        subquery = User.objects.filter(
            teams__in=teams,
            id=OuterRef("user_id"),
        )

        return queryset.annotate(user_is_team_member=Exists(subquery)).filter(
            user_is_team_member=True,
            approve_state=ApprovedState.CREATED,
        )


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


class WorkBreakFilterSet(django_filters.FilterSet):
    """Set of filters for Work Break."""

    class Meta:
        model = WorkBreak
        fields = ("approving", "team", "user")

    approving = ApprovingFilter()
    team = TeamFilter()
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())

    order_by = OrderingFilter(fields=("from_date",))
