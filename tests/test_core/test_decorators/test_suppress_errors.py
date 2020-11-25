from urllib.error import HTTPError, URLError

import pytest

from apps.core.decorators import suppress_errors


def test_suppress_errors():
    """Test decorator suppress_errors."""
    assert _zero_division1() is None
    assert _zero_division2() is None

    with pytest.raises(ZeroDivisionError):
        _zero_division3()

    assert _key_value_error("key") is None
    assert _key_value_error("value") is None

    with pytest.raises(SystemError):
        _key_value_error("error")

    assert _inherit_errors() is None


@suppress_errors(ZeroDivisionError)
def _zero_division1():
    return 1 / 0  # noqa: WPS344


@suppress_errors(Exception)
def _zero_division2():
    return 1 / 0  # noqa: WPS344


@suppress_errors(ValueError)
def _zero_division3():
    return 1 / 0  # noqa: WPS344


@suppress_errors(ValueError, KeyError)
def _key_value_error(error):
    exceptions = {
        "key": KeyError,
        "value": ValueError,
    }

    raise exceptions.get(error, SystemError)


@suppress_errors(URLError)
def _inherit_errors():
    raise HTTPError("www.test.com", 400, "test", None, None)
