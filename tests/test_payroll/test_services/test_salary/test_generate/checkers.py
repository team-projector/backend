from apps.payroll.models import Salary
from apps.skills.models import Position
from tests.helpers.checkers import assert_instance_fields


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
    assert_instance_fields(
        salary,
        charged_time=charged_time,
        sum=sum,
        penalty=penalty,
        bonus=bonus,
        taxes=taxes,
        hour_rate=hour_rate,
        tax_rate=tax_rate,
        position=position,
        total=total,
    )
