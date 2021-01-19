import django_filters
import graphene
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.fields import BaseModelConnectionField
from jnt_django_graphene_toolbox.filters import SortHandler

from apps.development.graphql.types.enums import MergeRequestState
from apps.development.models import MergeRequest, Project, Team, TeamMember
from apps.users.models import User


class TeamFilter(django_filters.ModelChoiceFilter):
    """Filter issues by team."""

    def __init__(self) -> None:
        """
        Initialize self.

        Set queryset.
        """
        super().__init__(queryset=Team.objects.all())

    def filter(  # noqa: WPS125
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering."""
        if not value:
            return queryset

        users = TeamMember.objects.get_no_watchers(value)
        return queryset.filter(user__in=users)


class MergeRequestSort(graphene.Enum):
    """Allowed sort fields."""

    TITLE_ASC = "title"  # noqa: WPS115
    TITLE_DESC = "-title"  # noqa: WPS115
    CREATED_AT_ASC = "created_at"  # noqa: WPS115
    CREATED_AT_DESC = "-created_at"  # noqa: WPS115
    CLOSED_AT_ASC = "closed_at"  # noqa: WPS115
    CLOSED_AT_DESC = "-closed_at"  # noqa: WPS115


class MergeRequestFilterSet(django_filters.FilterSet):
    """Set of filters for Merge Request."""

    class Meta:
        model = MergeRequest
        fields = "__all__"

    state = django_filters.CharFilter()
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    project = django_filters.ModelChoiceFilter(queryset=Project.objects.all())
    team = TeamFilter()


class MergeRequestsConnectionField(BaseModelConnectionField):
    """Handler for labels collections."""

    auth_required = True
    sort_handler = SortHandler(MergeRequestSort)
    filterset_class = MergeRequestFilterSet

    def __init__(self):
        """Initialize."""
        super().__init__(
            "apps.development.graphql.types.MergeRequestType",
            user=graphene.ID(),
            project=graphene.ID(),
            state=graphene.Argument(MergeRequestState),
            team=graphene.ID(),
        )
