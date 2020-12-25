from typing import List

from django.db import models
from jnt_django_graphene_toolbox.filters import (
    OrderingFilter as BaseOrderingFilter,
)

ORDER_FIELD = "-id"


class OrderingFilter(BaseOrderingFilter):
    """Custom ordering filter."""

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

        if ORDER_FIELD not in ordering_fields:
            self._append_order_field(ordering_fields)

        return super().filter(queryset, ordering_fields)

    def _add_order_field(self, kwargs) -> None:
        """Add order_field as enabled ordering field."""
        fields_field = "fields"
        kwargs.setdefault(fields_field, (ORDER_FIELD,))

        if ORDER_FIELD not in kwargs[fields_field]:
            kwargs[fields_field] = (*kwargs[fields_field], ORDER_FIELD)

    def _get_model_ordering(self, model: models.Model) -> List[str]:
        """Get default ordering for model."""
        return (
            list(model._meta.ordering)  # noqa: WPS437
            if model._meta.ordering  # noqa: WPS437
            else []
        )

    def _append_order_field(self, ordering: List[str]) -> None:
        """Append ordering field."""
        reverse_order = "-{0}".format(ORDER_FIELD).replace("--", "")
        if not {ORDER_FIELD, reverse_order} & set(ordering):
            ordering.append(ORDER_FIELD)
