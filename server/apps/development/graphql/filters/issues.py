import django_filters
from django.db.models import QuerySet

from apps.development.models import Issue, Team, TeamMember
from apps.users.models import User


class TeamFilter(django_filters.ModelChoiceFilter):
    def __init__(self) -> None:
        super().__init__(queryset=Team.objects.all())

    def filter(self, qs, value) -> QuerySet:
        if not value:
            return qs

        users = TeamMember.objects.get_no_watchers(value)
        return qs.filter(user__in=users)


class IssuesFilterSet(django_filters.FilterSet):
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    team = TeamFilter()

    order_by = django_filters.OrderingFilter(
        fields=('due_date', 'title', 'created_at')
    )

    class Meta:
        model = Issue
        fields = ('state', 'due_date', 'user', 'team')
