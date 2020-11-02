from datetime import date

import pytest
from django.utils import timezone

from tests.test_payroll.factories import WorkBreakFactory

CURRENT_YEAR = timezone.now().year


@pytest.mark.parametrize(
    ("from_date", "to_date", "paid_days"),
    [
        (
            date(CURRENT_YEAR, 2, 3),
            date(CURRENT_YEAR, 2, 10),
            7,
        ),
        (
            date(CURRENT_YEAR - 1, 12, 28),
            date(CURRENT_YEAR, 1, 3),
            2,
        ),
        (
            date(CURRENT_YEAR - 1, 12, 28),
            date(CURRENT_YEAR, 1, 1),
            0,
        ),
        (
            date(CURRENT_YEAR, 12, 27),
            date(CURRENT_YEAR + 1, 1, 3),
            5,
        ),
        (
            date(CURRENT_YEAR - 1, 1, 1),
            date(CURRENT_YEAR - 1, 2, 2),
            0,
        ),
        (
            date(CURRENT_YEAR + 1, 1, 1),
            date(CURRENT_YEAR + 1, 2, 2),
            0,
        ),
    ],
)
def test_fill(db, from_date, to_date, paid_days):
    """Test fill paid days."""
    work_break = WorkBreakFactory.create(
        from_date=from_date,
        to_date=to_date,
    )

    assert work_break.paid_days == paid_days


def test_not_fill(db):
    """Test not fill paid days."""
    work_break = WorkBreakFactory.create(
        from_date=date(CURRENT_YEAR - 1, 12, 28),
        to_date=date(CURRENT_YEAR, 1, 3),
        paid_days=1,
    )

    assert work_break.paid_days == 1
