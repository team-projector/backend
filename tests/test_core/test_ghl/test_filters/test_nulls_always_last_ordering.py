# -*- coding: utf-8 -*-

from django.utils import timezone
from django_filters import OrderingFilter as BaseOrderingFilter

from apps.core.graphql.filters.mixins import NullsAlwaysLastOrderingMixin
from apps.development.models import Issue
from tests.test_development.factories import IssueFactory


class TestFilter(NullsAlwaysLastOrderingMixin, BaseOrderingFilter):
    """Test ordering filter."""


def test_asc_ordering(db):
    """Test asc ordering case."""
    now = timezone.now()

    issues = [
        IssueFactory(due_date=now - timezone.timedelta(days=1)),
        IssueFactory(due_date=now),
        IssueFactory(due_date=None),
    ]

    test_filter = TestFilter(fields=(
        ('due_date',)
    ))

    queryset = test_filter.filter(
        Issue.objects.all(),
        value=['due_date'],
    )

    assert list(queryset) == issues


def test_desc_ordering(db):
    """Test desc ordering case."""
    now = timezone.now()

    issues = [
        IssueFactory(due_date=None),
        IssueFactory(due_date=now - timezone.timedelta(days=1)),
        IssueFactory(due_date=now),
    ]

    test_filter = TestFilter(fields=(
        ('due_date',)
    ))

    queryset = test_filter.filter(
        Issue.objects.all(),
        value=['-due_date'],
    )

    issues.reverse()

    assert list(queryset) == issues
