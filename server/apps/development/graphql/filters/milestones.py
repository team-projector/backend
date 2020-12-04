import django_filters
from jnt_django_graphene_toolbox.filters import OrderingFilter, SearchFilter

from apps.development.models import Project
from apps.development.models.milestone import Milestone


class ProjectFilter(django_filters.ModelChoiceFilter):
    """Project filter class."""

    def __init__(self, *args, **kwargs):
        """Init filter class."""
        kwargs.setdefault("queryset", Project.objects.all())
        super().__init__(*args, **kwargs)

    def filter(self, queryset, project):  # noqa: A003 WPS125
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
