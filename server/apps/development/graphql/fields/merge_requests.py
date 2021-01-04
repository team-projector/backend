import django_filters
import graphene
from django.db.models import QuerySet

from apps.core.graphql.fields import BaseModelConnectionField
from apps.core.graphql.queries.filters import OrderingFilter
from apps.development.models import MergeRequest, Project, Team, TeamMember
from apps.development.models.merge_request import MergeRequestState
from apps.users.models import User


class TeamFilter(django_filters.ModelChoiceFilter):
    """Filter issues by team."""

    def __init__(self) -> None:
        """
        Initialize self.

        Set queryset.
        """
        super().__init__(queryset=Team.objects.all())

    def filter(  # noqa: A003, WPS125
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering."""
        if not value:
            return queryset

        users = TeamMember.objects.get_no_watchers(value)
        return queryset.filter(user__in=users)


class MergeRequestFilterSet(django_filters.FilterSet):
    """Set of filters for Merge Request."""

    class Meta:
        model = MergeRequest
        fields = ("state", "user", "team", "project")

    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    project = django_filters.ModelChoiceFilter(queryset=Project.objects.all())
    team = TeamFilter()

    order_by = OrderingFilter(fields=("title", "created_at", "closed_at"))


class MergeRequestsConnectionField(BaseModelConnectionField):
    """Handler for labels collections."""

    filterset_class = MergeRequestFilterSet
    auth_required = True

    def __init__(self):
        """Initialize."""
        super().__init__(
            "apps.development.graphql.types.MergeRequestType",
            order_by=graphene.String(),
            user=graphene.ID(),
            project=graphene.ID(),
            state=graphene.Argument(
                graphene.Enum.from_enum(MergeRequestState),
            ),
            team=graphene.ID(),
        )