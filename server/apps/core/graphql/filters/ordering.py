from collections import OrderedDict

from django_filters import OrderingFilter
from graphene.utils.str_converters import to_camel_case


class CamelCasedOrderingFilter(OrderingFilter):
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
