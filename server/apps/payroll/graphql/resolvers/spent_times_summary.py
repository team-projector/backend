# -*- coding: utf-8 -*-

from apps.payroll.graphql.filters import SpentTimeFilterSet
from apps.payroll.models import SpentTime
from apps.payroll.services import spent_time as spent_time_service


def resolve_spent_times_summary(
    parent,
    info,
    **kwargs,
):
    """Resolve spent times summary."""
    filterset = SpentTimeFilterSet(
        data=kwargs,
        queryset=SpentTime.objects.allowed_for_user(
            info.context.user,
        ),
        request=info.context,
    )

    return spent_time_service.get_summary(
        filterset.qs,
    )
