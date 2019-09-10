from django.db.models import F


class NullsAlwaysLastOrderingMixin:
    def get_ordering_value(self, param):
        ord_value = super().get_ordering_value(param)  # type: ignore

        descending = ord_value.startswith('-')
        value = ord_value[1:] if descending else ord_value

        if descending:
            return F(value).desc(nulls_last=True)

        return F(value).asc(nulls_last=True)
