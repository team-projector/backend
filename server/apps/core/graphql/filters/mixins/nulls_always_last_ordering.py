from typing import TYPE_CHECKING, Any

from django.db.models import F
from django_filters import OrderingFilter

if TYPE_CHECKING:
    _Base: Any = OrderingFilter
else:
    _Base = object


class NullsAlwaysLastOrderingMixin(_Base):
    def get_ordering_value(self, param):
        ord_value = super().get_ordering_value(param)

        descending = ord_value.startswith('-')
        value = ord_value[1:] if descending else ord_value

        if descending:
            return F(value).desc(nulls_last=True)

        return F(value).asc(nulls_last=True)
