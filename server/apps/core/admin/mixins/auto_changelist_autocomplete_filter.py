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
    ):
        """Init autocomplete filter."""
        self.field_name = field_name
        self.title = field_name
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
