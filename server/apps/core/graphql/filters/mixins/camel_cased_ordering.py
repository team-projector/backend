from collections import OrderedDict
from typing import TYPE_CHECKING, Any

from django_filters import OrderingFilter
from graphene.utils.str_converters import to_camel_case

if TYPE_CHECKING:
    _Base: Any = OrderingFilter
else:
    _Base = object


class CamelCasedOrderingMixin(_Base):
    """
    ('user__due_date',) becomes => {'user__due_date': 'user__dueDate'}
    (('due_date', 'due_date'),) becomes => {'due_date': 'dueDate'}
    {'due_date': 'due_date'} becomes => {'due_date': 'dueDate'}
    """

    @classmethod
    def normalize_fields(cls, fields):
        ret = super().normalize_fields(fields)

        return OrderedDict([
            (k, '__'.join(to_camel_case(c) for c in v.split('__')))
            for k, v in
            ret.items()
        ])
