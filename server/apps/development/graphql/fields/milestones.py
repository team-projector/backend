import django_filters
import graphene
from django.db import models
from jnt_django_graphene_toolbox.fields import BaseModelConnectionField
from jnt_django_graphene_toolbox.filters import SearchFilter

from apps.core.graphql.queries.filters import OrderingFilter
from apps.development.graphql.types.enums import MilestoneState
from apps.development.models import Project
from apps.development.models.milestone import Milestone


class ProjectFilter(django_filters.ModelChoiceFilter):
    """Project filter class."""

    def __init__(self, *args, **kwargs) -> None:
        """Init filter class."""
        kwargs.setdefault("queryset", Project.objects.all())
        super().__init__(*args, **kwargs)

    def filter(  # noqa: A003 WPS125
        self,
        queryset,
        project,
    ) -> models.QuerySet:
        """Filter queryset by project."""
        if project:
            queryset = queryset.filter(id__in=project.milestones.all())

        return queryset


class MilestonesFilterSet(django_filters.FilterSet):
    """Set of filters for Milestone."""

    class Meta:
        model = Milestone
        fields = "__all__"

    project = ProjectFilter()
    q = SearchFilter(fields=("title", "=gl_url"))  # noqa: WPS111
    order_by = OrderingFilter(fields=("due_date",))


class MilestoneSort(graphene.Enum):
    """Allowed sort fields."""

    DUE_DATE_ASC = "due_date"  # noqa: WPS115
    DUE_DATE_DESC = "-due_date"  # noqa: WPS115


class MilestonesConnectionField(BaseModelConnectionField):
    """Handler for labels collections."""

    filterset_class = MilestonesFilterSet
    auth_required = True

    def __init__(self):
        """Initialize."""
        super().__init__(
            "apps.development.graphql.types.MilestoneType",
            order_by=graphene.Argument(graphene.List(MilestoneSort)),
            project=graphene.ID(),
            q=graphene.String(),
            state=graphene.Argument(MilestoneState),
        )
