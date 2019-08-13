from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from apps.development.services.allowed.team_progress_metrics import \
    is_allowed_for_user
from apps.payroll.services.metrics.progress.team import \
    get_team_progress_metrics, Team


def resolve_team_progress_metrics(parent, info, **kwargs):
    team = get_object_or_404(
        Team.objects.all(),
        pk=kwargs['team']
    )

    if not is_allowed_for_user(team, info.context.user):
        raise PermissionDenied

    return get_team_progress_metrics(
        team,
        kwargs['start'],
        kwargs['end'],
        kwargs['group']
    )
