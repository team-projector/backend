import django_filters
from django.db.models import QuerySet

from apps.development.models import MergeRequest, Team, TeamMember, Project
from apps.users.models import User


class TeamFilter(django_filters.ModelChoiceFilter):
    def __init__(self) -> None:
        super().__init__(queryset=Team.objects.all())

    def filter(self, queryset, value) -> QuerySet:
        if not value:
            return queryset

        users = TeamMember.objects.get_no_watchers(value)
        return queryset.filter(user__in=users)


class MergeRequestFilterSet(django_filters.FilterSet):
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    project = django_filters.ModelChoiceFilter(queryset=Project.objects.all())
    team = TeamFilter()

    order_by = django_filters.OrderingFilter(
        fields=('title', 'created_at')
    )

    class Meta:
        model = MergeRequest
        fields = ('state', 'user', 'team', 'project')
