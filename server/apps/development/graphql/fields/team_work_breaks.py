import django_filters
import graphene
from django.db.models import QuerySet

from apps.core.graphql.fields import BaseModelConnectionField
from apps.core.graphql.queries.filters import OrderingFilter
from apps.development.models import Team, TeamMember
from apps.payroll.graphql.types import WorkBreakType
from apps.users.models import User


def filter_allowed_for_user(
    queryset: QuerySet,
    user: User,
):
    """Filter work breaks for user."""
    users = TeamMember.objects.filter(
        user=user,
        roles=TeamMember.roles.LEADER,
    ).values_list("team__members", flat=True)

    return queryset.filter(user_id__in=(*users, user.id))


class UserFilter(django_filters.ModelChoiceFilter):
    """Filter workbreaks by user."""

    def __init__(self) -> None:
        """Initialize self."""
        super().__init__(queryset=User.objects.all())

    def filter(  # noqa: WPS125, A003
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering."""
        if not value:
            return queryset

        return queryset.filter(pk=value.pk)


class TeamFilter(django_filters.ModelChoiceFilter):
    """Filter workbreaks by team."""

    def __init__(self) -> None:
        """Initialize self."""
        super().__init__(queryset=Team.objects.all())

    def filter(  # noqa: WPS125, A003
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering."""
        if not value:
            return queryset

        users = TeamMember.objects.get_no_watchers(value)
        return queryset.filter(id__in=users)


class TeamWorkBreaksFilterSet(django_filters.FilterSet):
    """Set of filters for UserWorkBreak."""

    class Meta:
        model = User
        fields = ("name", "email")

    user = UserFilter()
    team = TeamFilter()

    order_by = OrderingFilter(fields=("name", "email"))

    def filter_queryset(self, queryset):
        """Filtering queryset."""
        queryset = super().filter_queryset(queryset)

        return filter_allowed_for_user(queryset, self.request.user)


class TeamWorkBreaksConnectionField(BaseModelConnectionField):
    """Handler for users collections."""

    filterset_class = TeamWorkBreaksFilterSet

    def __init__(self):
        """Initialize."""
        super().__init__(
            WorkBreakType,
            user=graphene.ID(),
            team=graphene.ID(),
            order_by=graphene.String(),  # "name", "email"
        )
