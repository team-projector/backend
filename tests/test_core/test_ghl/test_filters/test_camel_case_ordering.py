# -*- coding: utf-8 -*-

import pytest
from django_filters import OrderingFilter as BaseOrderingFilter

from apps.core.graphql.filters.mixins import CamelCasedOrderingMixin


class TestFilter(CamelCasedOrderingMixin, BaseOrderingFilter):
    """Test ordering filter."""


@pytest.mark.parametrize(('ordering', 'field'), [
    ('fieldI18n', 'field_i18n'),
    ('snakesOnA__plane', 'snakes_on_a__plane'),
    ('dueDate', 'due_date'),
    ('user__dueDate', 'user__due_date'),
])
def test_convert(ordering, field):
    """Test camel case filtering."""
    test_filter = TestFilter(fields=(
        field,
    ))

    assert test_filter.get_ordering_value(ordering) == field
