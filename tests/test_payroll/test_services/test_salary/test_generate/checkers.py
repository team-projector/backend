from apps.payroll.models import Salary
from apps.users.models import Position


def check_salary(  # noqa: WPS211
    salary: Salary,
    charged_time: int = 0,
    sum: float = 0,  # noqa: WPS125, A002
    penalty: float = 0,
    bonus: float = 0,
    taxes: float = 0,
    hour_rate: float = 0,
    tax_rate: float = 0,
    total: float = 0,
    position: Position = None,
):
    """Check salary."""
    assert salary.charged_time == charged_time
    assert salary.sum == sum
    assert salary.penalty == penalty
    assert salary.bonus == bonus
    assert salary.taxes == taxes
    assert salary.hour_rate == hour_rate
    assert salary.tax_rate == tax_rate
    assert salary.position == position
    assert salary.total == total
