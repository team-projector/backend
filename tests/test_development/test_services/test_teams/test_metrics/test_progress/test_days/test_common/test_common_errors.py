from datetime import datetime, timedelta

import pytest
from django.utils import timezone

from apps.development.services.team.metrics.progress import (
    get_progress_metrics,
)
from apps.development.services.team.metrics.progress.base import (
    ProgressMetricsProvider,
)
from tests.test_development.factories import TeamFactory


def test_bad_group(db):
    """
    Test bad group.

    :param db:
    """
    group = "test_bad_group"
    with pytest.raises(ValueError, match="Bad group '{0}'".format(group)):
        get_progress_metrics(
            TeamFactory.create(),
            timezone.now().date() - timedelta(days=5),
            timezone.now().date() + timedelta(days=5),
            group,
        )


def test_provider_not_implemented(user):
    """
    Test provider not implemented.

    :param user:
    """
    with pytest.raises(NotImplementedError):
        ProgressMetricsProvider(
            TeamFactory.create(),
            datetime.now().date() - timedelta(days=5),
            datetime.now().date() + timedelta(days=5),
        ).get_user_metrics(user)
