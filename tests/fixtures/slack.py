import pytest


@pytest.fixture()
def slack(override_config):  # noqa: PT004
    """Provide slack settings."""
    with override_config(SLACK_TOKEN="token"):
        yield
