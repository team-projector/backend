import django_filters
from django.db.models import QuerySet

from apps.development.models import Milestone, Team, TeamMember, Ticket
from apps.development.services.issue.allowed import check_allow_project_manager
from apps.development.services.issue.problems import (
    annotate_issue_problems,
    exclude_issue_problems,
    filter_issue_problems,
)
from apps.users.models import User


class CreatedByForOtherFilter(django_filters.ModelChoiceFilter):
    """
    Filter by author.

    Hide issues author himself and assigned to himself.
    """

    def __init__(self) -> None:
        """
        Initialize created by for other filter.

        Set queryset.
        """
        super().__init__(queryset=User.objects.all())

    def filter(  # noqa: WPS125
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering by author and exclude himself assignee."""
        if not value:
            return queryset

        return queryset.filter(author=value).exclude(user=value)


class TicketFilter(django_filters.ModelChoiceFilter):
    """Filter issues by ticket."""

    def __init__(self) -> None:
        """
        Initialize self.

        Set queryset.
        """
        super().__init__(queryset=Ticket.objects.all())

    def filter(  # noqa: WPS125
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering by ticket."""
        if not value:
            return queryset

        check_allow_project_manager(self.parent.request.user)

        return queryset.filter(ticket=value)


class MilestoneFilter(django_filters.ModelChoiceFilter):
    """Filter issues by milestone."""

    def __init__(self) -> None:
        """Initialize self."""
        super().__init__(queryset=Milestone.objects.all())

    def filter(  # noqa: WPS125
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering by milestone."""
        if not value:
            return queryset

        check_allow_project_manager(self.parent.request.user)

        return queryset.filter(milestone=value)


class ProblemsFilter(django_filters.BooleanFilter):
    """Filter issues by problem."""

    def filter(  # noqa: WPS125
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering by problem."""
        if value is None:
            return queryset

        queryset = annotate_issue_problems(queryset)

        if value is True:
            queryset = filter_issue_problems(queryset)
        elif value is False:
            queryset = exclude_issue_problems(queryset)

        return queryset


class TeamFilter(django_filters.ModelChoiceFilter):
    """Filter issues by team."""

    def __init__(self) -> None:
        """Initialize self."""
        super().__init__(queryset=Team.objects.all())

    def filter(  # noqa: WPS125
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering by team."""
        if not value:
            return queryset

        users = TeamMember.objects.get_no_watchers(value)
        return queryset.filter(user__in=users)
