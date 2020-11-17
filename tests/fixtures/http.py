import httpretty
import pytest


def version(socket):
    """
    Version - mock function.

    This function calling by urllib3.

    Return version of tls for httpretty fakesocket.
    """
    return "TLSv1.2"


setattr(httpretty.core.fakesock.socket, "version", version)  # noqa: B010


@pytest.fixture(autouse=True)
def _http_pretty(override_config) -> None:
    """Forces dissallow net connect."""
    httpretty.enable(allow_net_connect=False)
    httpretty.reset()
    yield

    httpretty.disable()
