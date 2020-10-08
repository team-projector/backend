import pytest
from django.core.exceptions import ValidationError

from apps.core.models.validators import tax_rate_validator

test_valid_data = [0, 0.5, 1]
test_not_valid_data = [-100, -1, -0.1, 1.001, 10, 100]


@pytest.mark.parametrize("tax_rate", test_valid_data)
def test_valid_tax_rate(tax_rate):
    """
    Test valid tax rate.

    :param tax_rate:
    """
    assert tax_rate_validator(tax_rate) is None


@pytest.mark.parametrize("tax_rate", test_not_valid_data)
def test_not_valid_tax_rate(tax_rate):
    """
    Test not valid tax rate.

    :param tax_rate:
    """
    with pytest.raises(ValidationError):
        tax_rate_validator(tax_rate)
