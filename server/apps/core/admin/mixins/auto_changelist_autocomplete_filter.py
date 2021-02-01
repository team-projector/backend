from functools import partial
from typing import Union

from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from jnt_admin_tools.autocomplete_filter import AutocompleteFilter


class AutoAutocompleteFilter(AutocompleteFilter):
    """Auto autocomplete filter."""

    def __init__(  # noqa: WPS211
        self,
        request,
        lookup_params,
        model,
        model_admin,
        field_name,
        is_multiple=False,
    ):
        """Init autocomplete filter."""
        self.field_name = field_name
        self.title = field_name
        self.is_multiple = is_multiple
        super().__init__(request, lookup_params, model, model_admin)


class AutoChangelistAutocompleteFilterMixin(admin.ModelAdmin):
    """Auto changelist autocomplete filter mixin."""

    def get_list_filter(self, request):
        """Get list filters."""
        list_filters = super().get_list_filter(request)
        return list(map(self._update_list_filter, list_filters))

    def _update_list_filter(self, list_filter) -> Union[str, object]:
        """Update list filter."""
        if self._list_filter_is_foreign(list_filter):
            return partial(AutoAutocompleteFilter, field_name=list_filter)
        elif self._list_filter_is_m2m(list_filter):
            return partial(
                AutoAutocompleteFilter,
                field_name=list_filter,
                is_multiple=True,
            )

        return list_filter

    def _list_filter_is_foreign(self, list_filter) -> bool:
        """Check list filter field is ForeignKey."""
        if not isinstance(list_filter, str):
            return False

        try:
            model_field = self.model._meta.get_field(  # noqa: WPS437
                list_filter,
            )
        except FieldDoesNotExist:
            return False

        return isinstance(model_field, models.ForeignKey)

    def _list_filter_is_m2m(self, list_filter) -> bool:
        """Check list filter field is ManyToMaany."""
        if not isinstance(list_filter, str):
            return False

        try:
            model_field = self.model._meta.get_field(  # noqa: WPS437
                list_filter,
            )
        except FieldDoesNotExist:
            return False

        return isinstance(model_field, models.ManyToManyField)
