# -*- coding: utf-8 -*-

from django_filters import OrderingFilter as BaseOrderingFilter

from apps.core.graphql.filters.mixins import CamelCasedOrderingMixin


class OrderingFilter(
    CamelCasedOrderingMixin,
    BaseOrderingFilter,
):
    """Test ordering filter."""


def test_camel_case():
    """Test camel case filtering."""
    filt = OrderingFilter(fields=(
        ('field_i18n', 'field_i18n'),
        'snakes_on_a__plane',
    ))

    assert filt.get_ordering_value('fieldI18n') == 'field_i18n'
    assert filt.get_ordering_value('snakesOnA__plane') == 'snakes_on_a__plane'


def test_camel_case_input_ad_dict():
    """Test camel case filtering with dict fields."""
    filt = OrderingFilter(fields={
        'due_date': 'due_date',
        'user__due_date': 'user__due_date',
    })

    assert filt.get_ordering_value('dueDate') == 'due_date'
    assert filt.get_ordering_value('user__dueDate') == 'user__due_date'
