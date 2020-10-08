from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from apps.core.graphql.helpers.generics import get_object_or_not_found
from apps.development.models import TeamMember
from apps.development.services.team_members import filter_by_roles
from apps.users.models import User
from apps.users.services.user.metrics import get_progress_metrics


def filter_allowed_for_user(queryset: QuerySet, user: User) -> QuerySet:
    """Get progress metrics for user."""
    allowed_users = filter_by_roles(
        TeamMember.objects.filter(user=user),
        [TeamMember.roles.LEADER, TeamMember.roles.WATCHER],
    ).values_list("team__members", flat=True)

    return queryset.filter(id__in={*allowed_users, user.id})


def resolve_user_progress_metrics(parent, info, **kwargs):  # noqa: WPS110
    """Resolve progress metrics for user."""
    user = get_object_or_not_found(
        filter_allowed_for_user(
            get_user_model().objects.all(),
            info.context.user,
        ),
        pk=kwargs["user"],
    )

    return get_progress_metrics(
        user,
        kwargs["start"],
        kwargs["end"],
        kwargs["group"],
    )
