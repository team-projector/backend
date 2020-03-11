# -*- coding: utf-8 -*-

from apps.core.graphql.helpers.generics import get_object_or_not_found
from apps.development.models import Team
from apps.development.services.team.allowed import (
    check_allow_get_metrics_by_user,
)
from apps.development.services.team.metrics.progress import (
    get_progress_metrics,
)


def resolve_team_progress_metrics(parent, info, **kwargs):  # noqa: WPS110
    """Resolve progress metrics for team."""
    team = get_object_or_not_found(Team.objects.all(), pk=kwargs["team"])

    check_allow_get_metrics_by_user(team, info.context.user)

    return get_progress_metrics(
        team, kwargs["start"], kwargs["end"], kwargs["group"],
    )
