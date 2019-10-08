# -*- coding: utf-8 -*-

from rest_framework.generics import get_object_or_404

from apps.development.models import Team
from apps.development.services import team as team_service
from apps.development.services.allowed.team_progress_metrics import (
    check_allow_get_metrics_by_user,
)


def resolve_team_progress_metrics(parent, info, **kwargs):
    """Resolve progress metrics for team."""
    team = get_object_or_404(
        Team.objects.all(),
        pk=kwargs['team'],
    )

    check_allow_get_metrics_by_user(team, info.context.user)

    return team_service.get_progress_metrics(
        team,
        kwargs['start'],
        kwargs['end'],
        kwargs['group'],
    )
