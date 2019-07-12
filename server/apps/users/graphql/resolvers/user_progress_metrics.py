from rest_framework.generics import get_object_or_404

from apps.payroll.services.metrics.progress.user import (
    get_user_progress_metrics, User
)


def resolve_user_progress_metrics(parent, info, **kwargs):
    user = get_object_or_404(
        User.objects.all(),
        pk=kwargs['user']
    )

    return get_user_progress_metrics(
        user,
        kwargs['start'],
        kwargs['end'],
        kwargs['group']
    )
