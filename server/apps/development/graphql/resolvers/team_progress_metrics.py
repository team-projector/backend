from rest_framework.generics import get_object_or_404

from apps.payroll.services.metrics.progress.team import \
    get_team_progress_metrics, Team


def resolve_team_progress_metrics(parent, info, **kwargs):
    team = get_object_or_404(
        Team.objects.all(),
        pk=kwargs['team']
    )

    return get_team_progress_metrics(
        team,
        kwargs['start'],
        kwargs['end'],
        kwargs['group']
    )
