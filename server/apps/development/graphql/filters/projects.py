import django_filters
import graphene
from django.forms import MultipleChoiceField
from graphene import List
from graphene_django.forms.converter import convert_form_field
from jnt_django_graphene_toolbox.filters import OrderingFilter, SearchFilter
from jnt_django_graphene_toolbox.filters.strings_array import (
    StringsArrayFilter,
)

from apps.development.models import Project
from apps.development.models.choices.project_state import ProjectState


class MultipleEnumChoiceField(MultipleChoiceField):
    """MultipleEnumChoiceField."""

    def __init__(self, enum, *args, **kwargs) -> None:
        """Init MultipleEnumChoiceField."""
        self.enum = enum
        kwargs["choices"] = enum.choices
        super().__init__(*args, **kwargs)


@convert_form_field.register(MultipleEnumChoiceField)
def convert_multiple_enum_choice_field(field):
    """Convert form field."""
    return List(graphene.Enum.from_enum(field.enum), required=field.required)


class ProjectStatesFilter(StringsArrayFilter):
    """Project states filter."""

    field_class = MultipleEnumChoiceField

    def __init__(self, *args, **kwargs) -> None:
        """Init project states filter."""
        kwargs.setdefault("lookup_expr", "in")
        super().__init__(*args, **kwargs)


class ProjectsFilterSet(django_filters.FilterSet):
    """Set of filters for projects."""

    class Meta:
        model = Project
        fields = ("title",)

    state = ProjectStatesFilter(enum=ProjectState)
    q = SearchFilter(fields=("title", "=gl_url"))  # noqa: WPS111
    order_by = OrderingFilter(fields=("title", "state", "full_title"))
