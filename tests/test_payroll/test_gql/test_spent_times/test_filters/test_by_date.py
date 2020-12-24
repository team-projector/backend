from datetime import date, timedelta

from django.utils import timezone
from jnt_django_toolbox.helpers.time import seconds

from apps.payroll.graphql.filters import SpentTimeFilterSet
from apps.payroll.models import SpentTime
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_filter_by_date(user, user2, issue):
    """
    Test filter by date.

    :param user:
    :param user2:
    :param issue:
    """
    spend_date = date(2020, 3, 3)

    IssueSpentTimeFactory.create(
        user=user2,
        base=issue,
        time_spent=int(seconds(minutes=10)),
        date=timezone.now() - timedelta(hours=1),
    )

    spends = {
        IssueSpentTimeFactory.create(
            user=user,
            base=issue,
            time_spent=int(seconds(hours=5)),
            date=spend_date,
        ),
        IssueSpentTimeFactory.create(
            user=user2,
            base=issue,
            time_spent=int(seconds(hours=2)),
            date=spend_date,
        ),
    }

    queryset = SpentTimeFilterSet(
        data={"date": "2020-03-03"},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert queryset.count() == 2
    assert set(queryset) == spends


def test_by_date_and_user(user, user2, issue):
    """
    Test by date and user.

    :param user:
    :param user2:
    :param issue:
    """
    spend_date = date(2019, 3, 3)

    IssueSpentTimeFactory.create(
        user=user2,
        base=issue,
        time_spent=int(seconds(hours=2)),
        date=spend_date,
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=3),
        user=user,
        base=issue,
        time_spent=int(seconds(hours=4)),
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user2,
        base=issue,
        time_spent=int(seconds(minutes=10)),
    )

    spend = IssueSpentTimeFactory.create(
        date=spend_date,
        user=user,
        base=issue,
        time_spent=int(seconds(hours=5)),
    )

    queryset = SpentTimeFilterSet(
        data={"date": "2019-03-03", "user": user.pk},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert queryset.count() == 1
    assert queryset[0] == spend
