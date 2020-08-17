# -*- coding: utf-8 -*-

from jnt_django_toolbox.helpers.time import seconds

from apps.development.models import Team
from apps.development.models.merge_request import MergeRequestState
from apps.development.services.team.metrics.main import get_team_metrics
from tests.test_development.factories import MergeRequestFactory
from tests.test_development.test_services.test_teams.test_metrics.test_common.checker import (  # noqa: E501
    check_team_metrics,
)


def test_basic(team: Team):
    """
    Test basic.

    :param team:
    :type team: Team
    """
    MergeRequestFactory.create_batch(
        2,
        user=team.members.all()[0],
        time_estimate=seconds(hours=2),
        state=MergeRequestState.OPENED,
    )
    MergeRequestFactory.create_batch(
        3,
        user=team.members.all()[0],
        time_estimate=seconds(hours=3),
        state=MergeRequestState.CLOSED,
    )
    MergeRequestFactory.create_batch(
        3,
        user=team.members.all()[1],
        time_estimate=seconds(hours=4),
        state=MergeRequestState.CLOSED,
    )

    MergeRequestFactory.create_batch(size=5)

    check_team_metrics(
        get_team_metrics(team),
        merge_requests_count=8,
        merge_requests_opened_count=2,
        merge_requests_opened_estimated=seconds(hours=4),
    )
