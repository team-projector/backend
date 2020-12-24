from datetime import timedelta

from django.utils import timezone
from jnt_django_toolbox.helpers.time import seconds

from apps.payroll.graphql.filters import SpentTimeFilterSet
from apps.payroll.models import SpentTime
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_filter_by_salary(user, user2, issue, salary):
    """
    Test filter by salary.

    :param user:
    :param user2:
    :param issue:
    :param salary:
    """
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=2),
        user=user2,
        base=issue,
        time_spent=int(seconds(hours=2)),
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user2,
        base=issue,
        time_spent=int(seconds(minutes=10)),
    )

    spends = {
        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=4),
            user=user,
            base=issue,
            time_spent=int(seconds(hours=5)),
            salary=salary,
        ),
        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=3),
            user=user,
            base=issue,
            time_spent=int(seconds(hours=4)),
            salary=salary,
        ),
    }

    queryset = SpentTimeFilterSet(
        data={"salary": salary.pk},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert queryset.count() == 2
    assert set(queryset) == spends


def test_filter_by_salary_not_exists(user, user2, issue, salary):
    """Will getting all TimeSpents, salary not exists will ignored."""
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=2),
        user=user2,
        base=issue,
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user2,
        base=issue,
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=4),
        user=user,
        base=issue,
        salary=salary,
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=3),
        user=user,
        base=issue,
        salary=salary,
    )

    queryset = SpentTimeFilterSet(
        data={"salary": salary.pk + 1},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert queryset.count() == 4
    assert set(queryset) == set(SpentTime.objects.all())
