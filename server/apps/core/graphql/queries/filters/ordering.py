from typing import List

from django.db import models
from django_filters import OrderingFilter as BaseOrderingFilter
from django_filters.fields import BaseCSVField
from django_filters.widgets import BaseCSVWidget

DEFAULT_ORDER_FIELD = "-id"


class SortWidget(BaseCSVWidget):
    """Sort widget."""

    def value_from_datadict(self, data, files, name):  # noqa: WPS110
        """Parse data from graphql."""
        sort_value = data.get(name)

        if sort_value is not None:
            if sort_value == "":  # empty value should parse as an empty list
                return []
            elif isinstance(sort_value, list):
                return sort_value
            return sort_value.split(",")
        return None


class SortField(BaseCSVField):
    """Custom sort field for overriding default."""

    widget = SortWidget


class OrderingFilter(BaseOrderingFilter):
    """Custom ordering filter."""

    base_field_class = SortField

    def __init__(self, *args, **kwargs) -> None:
        """Init ordering filter."""
        self._add_order_field(kwargs)
        super().__init__(*args, **kwargs)

    def filter(  # noqa: A003 WPS125
        self,
        queryset,
        ordering_fields,
    ) -> models.QuerySet:
        """Ordering queryset by fields."""
        ordering_fields = ordering_fields or []

        if not ordering_fields:
            ordering_fields = self._get_model_ordering(queryset.model)

        if DEFAULT_ORDER_FIELD not in ordering_fields:
            self._append_order_field(ordering_fields)

        return super().filter(queryset, ordering_fields)

    def _add_order_field(self, kwargs) -> None:
        """Add order_field as enabled ordering field."""
        fields_field = "fields"
        kwargs.setdefault(fields_field, (DEFAULT_ORDER_FIELD,))

        if DEFAULT_ORDER_FIELD not in kwargs[fields_field]:
            kwargs[fields_field] = (*kwargs[fields_field], DEFAULT_ORDER_FIELD)

    def _get_model_ordering(self, model: models.Model) -> List[str]:
        """Get default ordering for model."""
        return (
            list(model._meta.ordering)  # noqa: WPS437
            if model._meta.ordering  # noqa: WPS437
            else []
        )

    def _append_order_field(self, ordering: List[str]) -> None:
        """Append ordering field."""
        reverse_order = "-{0}".format(DEFAULT_ORDER_FIELD).replace("--", "")
        if not {DEFAULT_ORDER_FIELD, reverse_order} & set(ordering):
            ordering.append(DEFAULT_ORDER_FIELD)
