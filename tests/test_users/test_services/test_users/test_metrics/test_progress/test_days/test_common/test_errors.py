from datetime import datetime, timedelta

import pytest

from apps.users.services.user.metrics import get_progress_metrics
from apps.users.services.user.metrics.progress.provider import (
    ProgressMetricsProvider,
)


def test_bad_group(user):
    """
    Test bad group.

    :param user:
    """
    group = "test_bad_group"
    with pytest.raises(ValueError, match="Bad group '{0}'".format(group)):
        get_progress_metrics(
            user,
            datetime.now().date() - timedelta(days=5),
            datetime.now().date() + timedelta(days=5),
            group,
        )


def test_provider_not_implemented(user):
    """
    Test provider not implemented.

    :param user:
    """
    with pytest.raises(NotImplementedError):
        ProgressMetricsProvider(
            user,
            datetime.now().date() - timedelta(days=5),
            datetime.now().date() + timedelta(days=5),
        ).get_metrics()
