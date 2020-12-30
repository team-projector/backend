from datetime import timedelta

from django.utils import timezone
from jnt_django_toolbox.helpers.time import seconds

from apps.payroll.graphql.filters import SpentTimeFilterSet
from apps.payroll.models import SpentTime
from tests.helpers import lists
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_order_by_date(user, issue):
    """
    Test order by date.

    :param user:
    :param issue:
    """
    issue = IssueFactory.create()

    spends = [
        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(days=4),
            user=user,
            base=issue,
            time_spent=int(seconds(hours=5)),
        ),
        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(days=2),
            user=user,
            base=issue,
            time_spent=int(seconds(hours=2)),
        ),
        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(days=3),
            user=user,
            base=issue,
            time_spent=int(seconds(hours=4)),
        ),
        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(days=1),
            user=user,
            base=issue,
            time_spent=int(seconds(minutes=10)),
        ),
    ]

    queryset = SpentTimeFilterSet(
        data={"order_by": "date"},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert list(queryset) == lists.sub_list(spends, (0, 2, 1, 3))

    queryset = SpentTimeFilterSet(
        data={"order_by": "-date"},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert list(queryset) == lists.sub_list(spends, (3, 1, 2, 0))