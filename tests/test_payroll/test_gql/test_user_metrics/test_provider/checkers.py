def check_payroll(
    metrics,
    payroll_opened=0,
    payroll_closed=0,
) -> None:
    """
    Check payroll.

    :param metrics:
    :param payroll_opened:
    :param payroll_closed:
    """
    assert payroll_opened == metrics["payroll_opened"]
    assert payroll_closed == metrics["payroll_closed"]
    assert payroll_opened + payroll_closed == metrics["payroll"]


def check_taxes(
    metrics,
    taxes_opened=0,
    taxes_closed=0,
    taxes=0,
) -> None:
    """
    Check taxes.

    :param metrics:
    :param taxes_opened:
    :param taxes_closed:
    :param taxes:
    """
    assert taxes_opened == metrics["taxes_opened"]
    assert taxes_closed == metrics["taxes_closed"]
    assert taxes == metrics["taxes"]


def check_spent(  # noqa: WPS218
    metrics,
    issues_closed_spent=0,
    issues_opened_spent=0,
    mr_closed_spent=0,
    mr_opened_spent=0,
) -> None:
    """
    Check spent.

    :param metrics:
    :param issues_closed_spent:
    :param issues_opened_spent:
    :param mr_closed_spent:
    :param mr_opened_spent:
    """
    assert issues_closed_spent == metrics["issues"]["closed_spent"]
    assert issues_opened_spent == metrics["issues"]["opened_spent"]

    assert mr_closed_spent == metrics["merge_requests"]["closed_spent"]
    assert mr_opened_spent == metrics["merge_requests"]["opened_spent"]

    opened_spent = mr_opened_spent + issues_opened_spent
    closed_spent = mr_closed_spent + issues_closed_spent
    assert opened_spent == metrics["opened_spent"]
    assert closed_spent == metrics["closed_spent"]
