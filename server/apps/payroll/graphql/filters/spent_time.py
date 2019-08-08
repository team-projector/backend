import django_filters
from django.db.models import QuerySet

from apps.development.models import Project, Team, TeamMember
from apps.payroll.models import SpentTime
from apps.users.models import User


class TeamFilter(django_filters.ModelChoiceFilter):
    def __init__(self) -> None:
        super().__init__(queryset=Team.objects.all())

    def filter(self, queryset, value) -> QuerySet:
        if not value:
            return queryset

        users = TeamMember.objects.get_no_watchers(value)
        return queryset.filter(user__in=users)


class ProjectFilter(django_filters.ModelChoiceFilter):
    def __init__(self) -> None:
        super().__init__(queryset=Project.objects.all())

    def filter(self, queryset, value) -> QuerySet:
        if not value:
            return queryset

        return queryset.filter(
            issues__project=value
        ) | queryset.filter(
            mergerequests__project=value
        )


class SpentTimeFilterSet(django_filters.FilterSet):
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    project = ProjectFilter()
    team = TeamFilter()

    order_by = django_filters.OrderingFilter(
        fields=(
            ('date', 'date'),
            ('created_at', 'createdAt'),
        )
    )

    class Meta:
        model = SpentTime
        fields = ('date', 'user', 'salary', 'team')
