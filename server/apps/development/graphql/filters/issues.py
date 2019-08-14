import django_filters
from django.db.models import QuerySet

from apps.core.graphql.filters import SearchFilter
from apps.development.models import Issue, Milestone, Team, TeamMember, Project
from apps.development.services.problems.issue import (
    filter_issues_problems, exclude_issues_problems,
    annotate_issues_problems
)
from apps.development.services.allowed.issues import \
    check_allow_project_manager
from apps.users.models import User


class MilestoneFilter(django_filters.ModelChoiceFilter):
    def __init__(self) -> None:
        super().__init__(queryset=Milestone.objects.all())

    def filter(self, queryset, value) -> QuerySet:
        if not value:
            return queryset

        check_allow_project_manager(self.parent.request.user)

        return queryset.filter(milestone=value)


class MilestoneIssueOrphanFilter(django_filters.BooleanFilter):
    def filter(self, queryset, value) -> QuerySet:
        if value is None:
            return queryset

        check_allow_project_manager(self.parent.request.user)

        return queryset.filter(milestone__feature__isnull=value)


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


class TeamFilter(django_filters.ModelChoiceFilter):
    def __init__(self) -> None:
        super().__init__(queryset=Team.objects.all())

    def filter(self, queryset, value) -> QuerySet:
        if not value:
            return queryset

        users = TeamMember.objects.get_no_watchers(value)
        return queryset.filter(user__in=users)


class IssuesFilterSet(django_filters.FilterSet):
    milestone = MilestoneFilter()
    milestone_issue_orphan = MilestoneIssueOrphanFilter()
    problems = ProblemsFilter()
    project = django_filters.ModelChoiceFilter(queryset=Project.objects.all())
    team = TeamFilter()
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())

    order_by = django_filters.OrderingFilter(
        fields=('due_date', 'title', 'created_at')
    )

    q = SearchFilter(fields=('title',))

    class Meta:
        model = Issue
        fields = ('state', 'due_date', 'user', 'team', 'problems', 'project',
                  'milestone', 'milestone_issue_orphan')
