import django_filters
from django.db.models import QuerySet

from apps.development.models import Team, TeamMember
from apps.payroll.models import Salary
from apps.users.models import User

from apps.development.services.team_members import filter_by_roles
from rest_framework.exceptions import ValidationError


class TeamFilter(django_filters.ModelChoiceFilter):
    def __init__(self) -> None:
        super().__init__(queryset=Team.objects.all())

    def filter(self, queryset, value) -> QuerySet:
        if value:
            self._check_allowed_filtering(value)

        return queryset

    def _check_allowed_filtering(self, value):
        queryset = TeamMember.objects.filter(
            team=value,
            user=self.get_request().user
        )

        can_filtering = filter_by_roles(
            queryset,
            [
                TeamMember.roles.leader,
                TeamMember.roles.watcher
            ]
        ).exists()

        if not can_filtering:
            raise ValidationError('Can\'t filter by team')


class SalaryFilterSet(django_filters.FilterSet):
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    team = TeamFilter()

    order_by = django_filters.OrderingFilter(
        fields=('created_at',)
    )

    class Meta:
        model = Salary
        fields = ('user', 'team')
