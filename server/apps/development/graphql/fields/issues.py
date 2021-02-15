import django_filters
import graphene
from jnt_django_graphene_toolbox.fields import BaseModelConnectionField
from jnt_django_graphene_toolbox.filters import SearchFilter, SortHandler

from apps.development.graphql.fields.issues_filters import (
    CreatedByForOtherFilter,
    MilestoneFilter,
    ProblemsFilter,
    TeamFilter,
    TicketFilter,
)
from apps.development.graphql.types.enums import IssueState
from apps.development.models import Issue, Project
from apps.users.models import User


class IssueSort(graphene.Enum):
    """Allowed sort fields."""

    DUE_DATE_ASC = "due_date"  # noqa: WPS115
    DUE_DATE_DESC = "-due_date"  # noqa: WPS115
    TITLE_ASC = "title"  # noqa: WPS115
    TITLE_DESC = "-title"  # noqa: WPS115
    CREATED_AT_ASC = "created_at"  # noqa: WPS115
    CREATED_AT_DESC = "-created_at"  # noqa: WPS115
    CLOSED_AT_ASC = "closed_at"  # noqa: WPS115
    CLOSED_AT_DESC = "-closed_at"  # noqa: WPS115
    USER_ASC = "user"  # noqa: WPS115
    USER_DESC = "-user"  # noqa: WPS115
    STATE_ASC = "state"  # noqa: WPS115
    STATE_DESC = "-state"  # noqa: WPS115


class IssuesFilterSet(django_filters.FilterSet):
    """Set of filters for Issues."""

    class Meta:
        model = Issue
        fields = "__all__"

    milestone = MilestoneFilter()
    state = django_filters.CharFilter()
    problems = ProblemsFilter()
    due_date = django_filters.DateFilter()
    project = django_filters.ModelChoiceFilter(queryset=Project.objects.all())
    team = TeamFilter()
    ticket = TicketFilter()
    q = SearchFilter(fields=("title", "=gl_url"))  # noqa: WPS111
    created_by = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name="author",
    )
    assigned_to = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name="user",
    )
    participated_by = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name="participants",
    )
    created_by_for_other = CreatedByForOtherFilter()


class IssuesConnectionField(BaseModelConnectionField):
    """Handler for labels collections."""

    auth_required = True
    sort_handler = SortHandler(IssueSort)
    filterset_class = IssuesFilterSet

    def __init__(self):
        """Initialize."""
        super().__init__(
            "apps.development.graphql.types.IssueType",
            milestone=graphene.ID(),
            due_date=graphene.Date(),
            problems=graphene.Boolean(),
            project=graphene.ID(),
            team=graphene.ID(),
            ticket=graphene.ID(),
            q=graphene.String(),
            state=graphene.Argument(IssueState),
            created_by=graphene.ID(),
            assigned_to=graphene.ID(),
            participated_by=graphene.ID(),
            createdByForOther=graphene.ID(),
        )
