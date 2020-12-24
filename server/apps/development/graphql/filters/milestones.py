import django_filters
from django.db import models
from jnt_django_graphene_toolbox.filters import SearchFilter

from apps.core.graphql.queries.filters import OrderingFilter
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
        fields = ("state",)

    project = ProjectFilter()
    q = SearchFilter(fields=("title", "=gl_url"))  # noqa: WPS111
    order_by = OrderingFilter(fields=("due_date",))
