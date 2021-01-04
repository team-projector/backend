import django_filters
import graphene
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.filters import SearchFilter

from apps.core.graphql.fields import BaseModelConnectionField
from apps.core.graphql.queries.filters import OrderingFilter
from apps.development.models import (
    Issue,
    Milestone,
    Project,
    Team,
    TeamMember,
    Ticket,
)
from apps.development.models.issue import IssueState
from apps.development.services.issue.allowed import check_allow_project_manager
from apps.development.services.issue.problems import (
    annotate_issue_problems,
    exclude_issue_problems,
    filter_issue_problems,
)
from apps.users.models import User


class TicketFilter(django_filters.ModelChoiceFilter):
    """Filter issues by ticket."""

    def __init__(self) -> None:
        """
        Initialize self.

        Set queryset.
        """
        super().__init__(queryset=Ticket.objects.all())

    def filter(  # noqa: A003, WPS125
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

    def filter(  # noqa: A003, WPS125
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

    def filter(  # noqa: A003, WPS125
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

    def filter(  # noqa: A003, WPS125
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering by team."""
        if not value:
            return queryset

        users = TeamMember.objects.get_no_watchers(value)
        return queryset.filter(user__in=users)


class IssuesFilterSet(django_filters.FilterSet):
    """Set of filters for Issues."""

    class Meta:
        model = Issue
        fields = "__all__"

    milestone = MilestoneFilter()
    problems = ProblemsFilter()
    due_date = django_filters.DateFilter()
    project = django_filters.ModelChoiceFilter(queryset=Project.objects.all())
    team = TeamFilter()
    ticket = TicketFilter()
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    order_by = OrderingFilter(
        fields=(
            "due_date",
            "title",
            "created_at",
            "closed_at",
            "user",
            "state",
        ),
    )
    q = SearchFilter(fields=("title", "=gl_url"))  # noqa: WPS111


class IssuesConnectionField(BaseModelConnectionField):
    """Handler for labels collections."""

    filterset_class = IssuesFilterSet
    auth_required = True

    def __init__(self):
        """Initialize."""
        super().__init__(
            "apps.development.graphql.types.IssueType",
            order_by=graphene.String(),
            user=graphene.ID(),
            milestone=graphene.ID(),
            due_date=graphene.Date(),
            problems=graphene.Boolean(),
            project=graphene.ID(),
            team=graphene.ID(),
            ticket=graphene.ID(),
            q=graphene.String(),
            state=graphene.Argument(
                graphene.Enum.from_enum(IssueState),
            ),
        )