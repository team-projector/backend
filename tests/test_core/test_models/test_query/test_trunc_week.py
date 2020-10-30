import calendar
from datetime import datetime, timedelta

import pytest
from constance import config
from constance.test import override_config
from jnt_django_toolbox.helpers.date import begin_of_week

from apps.core.models.query import TruncWeek
from apps.payroll.models import SpentTime
from tests.test_payroll.factories import IssueSpentTimeFactory

ONE_WEEK = timedelta(weeks=1)


@pytest.fixture(
    params=[
        calendar.MONDAY,
        calendar.TUESDAY,
        calendar.WEDNESDAY,
        calendar.THURSDAY,
        calendar.FRIDAY,
        calendar.SATURDAY,
        calendar.SUNDAY,
    ],
)
def user(user, request):
    """Override config for user."""
    with override_config(FIRST_WEEK_DAY=request.param):
        yield user


def test_trunc_week(user):
    """Test trunc week as 'begin_of_week'."""
    start_week = begin_of_week(datetime.now().date(), config.FIRST_WEEK_DAY)
    spent_times = _create_spent_times(user, start_week)
    _assert_spent_times(spent_times, start_week)


def _create_spent_times(user, start_week):
    """Create spent times."""
    return [
        IssueSpentTimeFactory.create(user=user, date=start_week - ONE_WEEK),
        IssueSpentTimeFactory.create(user=user, date=start_week),
        IssueSpentTimeFactory.create(user=user, date=start_week + ONE_WEEK),
    ]


def _assert_spent_times(spent_times, start_week):
    """Assert spent times."""
    queryset = SpentTime.objects.annotate(week=TruncWeek("date"))

    assert queryset.get(pk=spent_times[0].pk).week == start_week - ONE_WEEK
    assert queryset.get(pk=spent_times[1].pk).week == start_week
    assert queryset.get(pk=spent_times[2].pk).week == start_week + ONE_WEEK
