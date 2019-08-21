from django.db.models import F
from django_filters import OrderingFilter


class NullsAlwaysLastOrderingFilter(OrderingFilter):
    def get_ordering_value(self, param):
        descending = param.startswith('-')
        param = param[1:] if descending else param
        field_name = self.param_map.get(param, param)

        return F(field_name).desc(nulls_last=True) if descending else F(field_name).asc(nulls_last=True)
