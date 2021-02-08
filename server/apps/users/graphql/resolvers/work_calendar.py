from jnt_django_graphene_toolbox.helpers.generics import (
    get_object_or_not_found,
)

from apps.core.graphql.security.authentication import auth_required
from apps.users.graphql.resolvers.user_progress_metrics import (
    filter_allowed_for_user,
)
from apps.users.models import User
from apps.users.services.user.work_calendar import get_work_calendar


def resolve_work_calendar(parent, info, **kwargs):  # noqa: WPS110
    """Resolve progress metrics for user."""
    auth_required(info)

    user = get_object_or_not_found(
        filter_allowed_for_user(
            User.objects.all(),
            info.context.user,
        ),
        pk=kwargs["user"],
    )

    return get_work_calendar(
        user,
        kwargs["start"],
        kwargs["end"],
    )
