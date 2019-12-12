from django.utils import timezone
from django_filters import OrderingFilter as BaseOrderingFilter

from apps.core.graphql.filters.mixins import NullsAlwaysLastOrderingMixin
from apps.development.models import Issue
from tests.test_development.factories import IssueFactory


class OrderingFilter(NullsAlwaysLastOrderingMixin, BaseOrderingFilter):
    """Test ordering filter."""


def test_nulls_last_asc(db):
    now = timezone.now()
    obj1 = IssueFactory(due_date=now)
    obj2 = IssueFactory(due_date=None)
    obj3 = IssueFactory(due_date=now - timezone.timedelta(days=1))

    f = OrderingFilter(fields=(
        ('due_date',)
    ))

    qs = f.filter(Issue.objects.values_list('id', flat=True),
                  value=['due_date'])

    assert list(qs) == [obj3.id, obj1.id, obj2.id]


def test_nulls_last_desc(db):
    now = timezone.now()
    obj1 = IssueFactory(due_date=now)
    obj2 = IssueFactory(due_date=None)
    obj3 = IssueFactory(due_date=now - timezone.timedelta(days=1))

    f = OrderingFilter(fields=(
        ('due_date',)
    ))

    qs = f.filter(Issue.objects.values_list('id', flat=True),
                  value=['-due_date'])

    assert list(qs) == [obj1.id, obj3.id, obj2.id]
