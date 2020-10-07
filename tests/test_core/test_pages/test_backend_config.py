from http import HTTPStatus

from apps.core.pages.views.backend_config import CACHE_CONTROL_MAX_AGE
from apps.core.services import backend_config


def test_backend_config(client):
    """Check config content and response headers."""
    response = client.get("/backend/config.js")

    assert response.status_code == HTTPStatus.OK
    assert response["Cache-Control"] == "max-age={0}".format(
        CACHE_CONTROL_MAX_AGE,
    )
    assert response["Content-Type"] == "text/javascript"
    assert response.content == backend_config.get_config().encode()
