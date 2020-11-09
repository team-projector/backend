from typing import Dict, Optional

from django import forms
from django.contrib.admin.widgets import AutocompleteSelect
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.fields.related import RelatedField
from jnt_admin_tools.autocomplete_filter import AutocompleteFilter

from apps.development.models import Project, ProjectGroup

OWNER_TYPES_MAP = {  # noqa: WPS407
    Project: "project",
    ProjectGroup: "project_group",
}


class OwnerFilter(AutocompleteFilter):
    """Autocomplete filter by owner."""

    field_name = "object_id"
    used_parameters: Dict[str, str] = {}

    def __init__(
        self,
        request,
        params,  # noqa: WPS110
        model,
        model_admin,
    ) -> None:
        """Initialize owner filter."""
        self.lookup_choices = ()
        self.parameter_name = "{0}__exact".format(self.field_name)

        if self.parameter_name in params:
            self.used_parameters[self.parameter_name] = params.pop(
                self.parameter_name,
            )

        content_type = request.GET.get("content_type__id__exact")

        if not content_type:  # patch for __init__
            return
        self._content_type_value = self._get_content_type_value(content_type)

        if not self._content_type_value:
            return

        self._update_title()
        self._generate_widget(model, model_admin)

    def get_field_queryset(self) -> models.QuerySet:
        """Get queryset for field autocomplete."""
        return self._content_type_value.objects.all()  # type: ignore

    def _generate_widget(self, model, model_admin) -> None:
        """Generate foreign key widget for generic field."""
        if self.rel_model:
            model = self.rel_model

        remote_field = self._get_remote_field(model)

        attrs = self.widget_attrs.copy()

        field = forms.ModelChoiceField(
            queryset=self.get_field_queryset(),
            widget=AutocompleteSelect(remote_field, model_admin.admin_site),
            required=False,
        )

        self._add_media(model_admin)

        self.rendered_widget = field.widget.render(
            name=self.parameter_name,
            value=self.used_parameters.get(self.parameter_name, ""),
            attrs=attrs,
        )

    def _get_content_type_value(self, content_type) -> Optional[models.Model]:
        """Get model by content type id."""
        try:
            content_type_value = ContentType.objects.get_for_id(content_type)
        except (ValueError, ContentType.DoesNotExist):
            return None

        return content_type_value.model_class()

    def _get_remote_field(self, model) -> RelatedField:
        """Get remote field."""
        field_name = OWNER_TYPES_MAP.get(self._content_type_value, "")

        return model._meta.get_field(field_name).remote_field  # noqa: WPS437

    def _update_title(self) -> None:
        """Update filter title."""
        present = OWNER_TYPES_MAP.get(self._content_type_value, "owner")
        self.title = present.replace("_", " ")
