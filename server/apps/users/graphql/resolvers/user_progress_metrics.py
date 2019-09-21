from rest_framework.generics import get_object_or_404

from apps.payroll.services.metrics.progress.user import (
    get_user_progress_metrics, User,
)
from apps.users.services.allowed.user_progress_metrics import (
    filter_allowed_for_user,
)


def resolve_user_progress_metrics(parent, info, **kwargs):
    user = get_object_or_404(
        filter_allowed_for_user(
            User.objects.all(), info.context.user,
        ),
        pk=kwargs['user'],
    )

    return get_user_progress_metrics(
        user,
        kwargs['start'],
        kwargs['end'],
        kwargs['group'],
    )
