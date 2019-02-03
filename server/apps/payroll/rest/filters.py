from datetime import date

import django_filters
from django_filters import rest_framework as filters

from apps.payroll.models import SpentTime


def filter_datetime_by_date(queryset, name, value: date):
    lookup = {
        f'{name}__year': value.year,
        f'{name}__month': value.month,
        f'{name}__day': value.day,
    }
    return queryset.filter(**lookup)


class SpentTimeFilter(filters.FilterSet):
    date = django_filters.DateFilter(field_name='date', method=filter_datetime_by_date)

    class Meta:
        model = SpentTime
        fields = ('employee', 'date')
