from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.helpers.generics import (
    get_object_or_not_found,
)

from apps.core.graphql.security.authentication import auth_required
from apps.development.models import TeamMember
from apps.development.services.team_members.filters import filter_by_roles
from apps.users.logic.services.user.progress import GroupProgressMetrics
from apps.users.logic.services.user.progress.main import get_progress_metrics
from apps.users.models import User


def filter_allowed_for_user(queryset: QuerySet, user: User) -> QuerySet:
    """Get progress metrics for user."""
    allowed_users = filter_by_roles(
        TeamMember.objects.filter(user=user),
        [TeamMember.roles.LEADER, TeamMember.roles.WATCHER],
    ).values_list("team__members", flat=True)

    return queryset.filter(id__in={*allowed_users, user.id})


def resolve_user_progress_metrics(parent, info, **kwargs):  # noqa: WPS110
    """Resolve progress metrics for user."""
    auth_required(info)

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
        GroupProgressMetrics(kwargs["group"]),
    )
