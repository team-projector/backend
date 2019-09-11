import django_filters
from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from apps.core.graphql.filters import SearchFilter
from apps.core.graphql.filters.ordering import OrderingFilter
from ...models import Issue, Ticket, Milestone, Team, TeamMember, Project
from ...services.allowed.issues import check_allow_project_manager
from ...services.problems.issue import (
    filter_issues_problems, exclude_issues_problems,
    annotate_issues_problems
)

User = get_user_model()


class TicketFilter(django_filters.ModelChoiceFilter):
    def __init__(self) -> None:
        super().__init__(queryset=Ticket.objects.all())

    def filter(self, queryset, value) -> QuerySet:
        if not value:
            return queryset

        check_allow_project_manager(self.parent.request.user)

        return queryset.filter(ticket=value)


class MilestoneFilter(django_filters.ModelChoiceFilter):
    def __init__(self) -> None:
        super().__init__(queryset=Milestone.objects.all())

    def filter(self, queryset, value) -> QuerySet:
        if not value:
            return queryset

        check_allow_project_manager(self.parent.request.user)

        return queryset.filter(milestone=value)


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
    problems = ProblemsFilter()
    project = django_filters.ModelChoiceFilter(queryset=Project.objects.all())
    team = TeamFilter()
    ticket = TicketFilter()
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())

    order_by = OrderingFilter(
        fields=('due_date', 'title', 'created_at', 'closed_at')
    )

    q = SearchFilter(fields=('title',))

    class Meta:
        model = Issue
        fields = (
            'state', 'due_date', 'user', 'team', 'problems', 'project',
            'milestone', 'ticket'
        )
