from datetime import date, datetime, timedelta

from django.utils import timezone

from apps.users.services.user import metrics
from tests.test_payroll.factories import WorkBreakFactory


def test_paid_work_breaks_days(user, ghl_auth_mock_info):
    """
    Test paid work breaks days.

    :param user:
    :param ghl_auth_mock_info:
    """
    now = datetime.now().date()
    WorkBreakFactory(
        user=user,
        paid=True,
        to_date=now,
        from_date=now - timedelta(days=5),
        paid_days=5,
    )
    paid_work_breaks_days = metrics.paid_work_breaks_days_resolver(user)
    assert paid_work_breaks_days == 5


def test_paid_work_breaks_days_not_paid_not_count(user, ghl_auth_mock_info):
    """
    Test paid work breaks days not paid not count.

    :param user:
    :param ghl_auth_mock_info:
    """
    now = timezone.now()
    WorkBreakFactory(
        user=user,
        paid=False,
        to_date=now,
        from_date=now - timedelta(days=5),
    )
    paid_work_breaks_days = metrics.paid_work_breaks_days_resolver(user)
    assert paid_work_breaks_days == 0


def test_paid_work_breaks_days_not_this_year(
    user,
    ghl_auth_mock_info,
):
    """
    Test paid work breaks days not this year.

    :param user:
    :param ghl_auth_mock_info:
    """
    now = datetime.now().date()
    WorkBreakFactory(
        user=user,
        paid=True,
        to_date=now - timedelta(days=370),
        from_date=now - timedelta(days=375),
    )
    paid_work_breaks_days = metrics.paid_work_breaks_days_resolver(user)
    assert paid_work_breaks_days == 0


def test_paid_work_breaks_lower_boundary_of_year(user, ghl_auth_mock_info):
    """
    Test paid work breaks lower boundary of year.

    :param user:
    :param ghl_auth_mock_info:
    """
    now = datetime.now().date()
    WorkBreakFactory(
        user=user,
        paid=True,
        to_date=date(now.year, 1, 3),
        from_date=date(now.year - 1, 12, 25),
        paid_days=2,
    )
    paid_work_breaks_days = metrics.paid_work_breaks_days_resolver(user)
    assert paid_work_breaks_days == 2


def test_paid_work_breaks_upper_boundary_of_year(user, ghl_auth_mock_info):
    """
    Test paid work breaks upper boundary of year.

    :param user:
    :param ghl_auth_mock_info:
    """
    now = timezone.now()
    WorkBreakFactory(
        user=user,
        paid=True,
        to_date=date(now.year + 1, 1, 3),
        from_date=date(now.year, 12, 25),
        paid_days=7,
    )
    paid_work_breaks_days = metrics.paid_work_breaks_days_resolver(user)
    assert paid_work_breaks_days == 7
