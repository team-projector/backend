# -*- coding: utf-8 -*-

from rest_framework.generics import get_object_or_404

from apps.development.services.allowed.team_progress_metrics import (
    check_allow_get_metrics_by_user,
)
from apps.payroll.services.metrics.progress.team import (
    get_team_progress_metrics, Team,
)


def resolve_team_progress_metrics(parent, info, **kwargs):
    team = get_object_or_404(
        Team.objects.all(),
        pk=kwargs['team'],
    )

    check_allow_get_metrics_by_user(team, info.context.user)

    return get_team_progress_metrics(
        team,
        kwargs['start'],
        kwargs['end'],
        kwargs['group'],
    )
