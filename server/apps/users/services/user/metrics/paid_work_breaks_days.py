from django.db import models
from django.db.models.functions import Coalesce
from django.utils.timezone import now

from apps.payroll.models import WorkBreak


def paid_work_breaks_days_resolver(
    parent,
    info,  # noqa: WPS110
    **kwargs,
) -> int:
    """Returns overall paid work break days for user."""
    user = info.context.user
    if not user.is_authenticated:
        return 0

    current_year = now().year

    return WorkBreak.objects.filter(
        models.Q(to_date__year=current_year)
        | models.Q(from_date__year=current_year),
        user=user,
        paid=True,
    ).aggregate(total_paid_days=Coalesce(models.Sum("paid_days"), 0))[
        "total_paid_days"
    ]
