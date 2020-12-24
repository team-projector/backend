from django.db import models
from jnt_django_graphene_toolbox.filters import (
    OrderingFilter as BaseOrderingFilter,
)

ORDER_FIELD = "id"


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
        if ORDER_FIELD not in ordering_fields:
            ordering_fields.append(ORDER_FIELD)

        return super().filter(queryset, ordering_fields)

    def _add_order_field(self, kwargs) -> None:
        """Add order_field as enabled ordering field."""
        fields_field = "fields"
        kwargs.setdefault(fields_field, (ORDER_FIELD,))

        if ORDER_FIELD not in kwargs[fields_field]:
            kwargs[fields_field] = (*kwargs[fields_field], ORDER_FIELD)
