import pytest

from apps.payroll.models import Payroll


@pytest.fixture(scope="session")
def payroll_admin(admin_registry):
    """
    Payroll admin.

    :param admin_registry:
    """
    return admin_registry[Payroll]
