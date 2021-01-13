import django_filters
import graphene
from django.db.models import Exists, OuterRef, QuerySet
from jnt_django_graphene_toolbox.fields import BaseModelConnectionField
from jnt_django_graphene_toolbox.filters import SortHandler

from apps.development.models import TeamMember
from apps.payroll.models import WorkBreak
from apps.payroll.models.mixins.approved import ApprovedState
from apps.users.models import User


class ApprovingFilter(django_filters.BooleanFilter):
    """Filter work breaks by approved state."""

    def filter(  # noqa: A003, WPS125
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering."""
        if not value:
            return queryset

        teams = TeamMember.objects.filter(
            user=self.parent.request.user,
            roles=TeamMember.roles.LEADER,
        ).values_list("team", flat=True)

        subquery = User.objects.filter(
            teams__in=teams,
            id=OuterRef("user_id"),
        )

        return queryset.annotate(user_is_team_member=Exists(subquery)).filter(
            user_is_team_member=True,
            approve_state=ApprovedState.CREATED,
        )


class FromDateFilter(django_filters.DateFilter):
    """Filter work breaks by from date."""

    def filter(  # noqa: A003, WPS125
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering."""
        if not value:
            return queryset

        return queryset.filter(to_date__gte=value)


class ToDateFilter(django_filters.DateFilter):
    """Filter work breaks by to date."""

    def filter(  # noqa: A003, WPS125
        self,
        queryset,
        value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering."""
        if not value:
            return queryset

        return queryset.filter(from_date__lte=value)


class WorkBreakSort(graphene.Enum):
    """Allowed sortings."""

    FROM_DATE_ASC = "from_date"  # noqa: WPS115
    FROM_DATE_DESC = "-from_date"  # noqa: WPS115
    TO_DATE_ASC = "to_date"  # noqa: WPS115
    TO_DATE_DESC = "-to_date"  # noqa: WPS115


class WorkBreakFilterSet(django_filters.FilterSet):
    """Set of filters for Work Break."""

    class Meta:
        model = WorkBreak
        fields = "__all__"

    approving = ApprovingFilter()
    from_date = FromDateFilter()
    to_date = ToDateFilter()


class BaseWorkBreaksConnectionField(BaseModelConnectionField):
    """Handler for workbreaks collections."""

    auth_required = True
    sort_handler = SortHandler(WorkBreakSort)
    filterset_class = WorkBreakFilterSet

    def __init__(self, **kwargs):
        """Initialize."""
        super().__init__(
            "apps.payroll.graphql.types.WorkBreakType",
            **kwargs,
            approving=graphene.Boolean(),
            from_date=graphene.Date(),
            to_date=graphene.Date(),
        )
