from jnt_django_graphene_toolbox.helpers.generics import (
    get_object_or_not_found,
)

from apps.core.graphql.security.authentication import auth_required
from apps.development.models import Team
from apps.development.services.team.allowed import (
    check_allow_get_metrics_by_user,
)
from apps.development.services.team.metrics.progress import (
    get_progress_metrics,
)
from apps.users.services.user.metrics.progress.main import GroupProgressMetrics


def resolve_team_progress_metrics(parent, info, **kwargs):  # noqa: WPS110
    """Resolve progress metrics for team."""
    auth_required(info)

    team = get_object_or_not_found(Team.objects.all(), pk=kwargs["team"])

    check_allow_get_metrics_by_user(team, info.context.user)

    return get_progress_metrics(
        team,
        kwargs["start"],
        kwargs["end"],
        GroupProgressMetrics(kwargs["group"]),
    )
