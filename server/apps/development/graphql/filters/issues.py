import django_filters
from django.db.models import QuerySet

from apps.core.graphql.filters import SearchFilter
from apps.development.models import Issue, Team, TeamMember, Project
from apps.development.services.problems.issue import (
    filter_issues_problems, exclude_issues_problems,
    annotate_issues_problems
)
from apps.users.models import User


class TeamFilter(django_filters.ModelChoiceFilter):
    def __init__(self) -> None:
        super().__init__(queryset=Team.objects.all())

    def filter(self, queryset, value) -> QuerySet:
        if not value:
            return queryset

        users = TeamMember.objects.get_no_watchers(value)
        return queryset.filter(user__in=users)


class ProblemsFilter(django_filters.BooleanFilter):
    def filter(self, queryset, value) -> QuerySet:
        if value is None:
            return queryset

        queryset = annotate_issues_problems(queryset)

        if value is True:
            queryset = filter_issues_problems(queryset)
        elif value is False:
            queryset = exclude_issues_problems(queryset)

        return queryset


class IssuesFilterSet(django_filters.FilterSet):
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    project = django_filters.ModelChoiceFilter(queryset=Project.objects.all())
    team = TeamFilter()
    problems = ProblemsFilter()
    q = SearchFilter(fields=('title',))
    milestone_issue_orphan = django_filters.BooleanFilter(
        field_name='milestone', lookup_expr='feature__isnull'
    )

    order_by = django_filters.OrderingFilter(
        fields=('due_date', 'title', 'created_at')
    )

    class Meta:
        model = Issue
        fields = ('state', 'due_date', 'user', 'team', 'problems', 'project')
