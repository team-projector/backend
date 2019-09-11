import django_filters
from django.db.models import Exists, OuterRef, QuerySet

from apps.core.graphql.filters.ordering import OrderingFilter
from apps.development.models import Team, TeamMember
from apps.payroll.models.mixins.approved import CREATED
from apps.payroll.models import WorkBreak
from apps.payroll.services.allowed.work_break import (
    check_allow_filtering_by_team
)
from apps.users.models import User


class ApprovingFilter(django_filters.BooleanFilter):
    def filter(self, queryset, value) -> QuerySet:
        if not value:
            return queryset

        teams = TeamMember.objects.filter(
            user=self.parent.request.user,
            roles=TeamMember.roles.leader
        ).values_list(
            'team',
            flat=True
        )

        subquery = User.objects.filter(
            teams__in=teams,
            id=OuterRef('user_id')
        )

        queryset = queryset.annotate(
            user_is_team_member=Exists(subquery)
        ).filter(
            user_is_team_member=True,
            approve_state=CREATED
        )

        return queryset


class TeamFilter(django_filters.ModelChoiceFilter):
    def __init__(self) -> None:
        super().__init__(queryset=Team.objects.all())

    def filter(self, queryset, value) -> QuerySet:
        if not value:
            return queryset

        check_allow_filtering_by_team(value, self.parent.request.user)

        return queryset.filter(user__teams=value)


class WorkBreakFilterSet(django_filters.FilterSet):
    approving = ApprovingFilter()
    team = TeamFilter()
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())

    order_by = OrderingFilter(
        fields=('from_date',)
    )

    class Meta:
        model = WorkBreak
        fields = ('approving', 'team', 'user')
