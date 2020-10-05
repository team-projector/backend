# -*- coding: utf-8 -*-

from apps.payroll.graphql.filters import SpentTimeFilterSet
from apps.payroll.models import SpentTime
from apps.payroll.services import spent_time as spent_time_service
from apps.payroll.services.spent_time.allowed import filter_allowed_for_user


def resolve_spent_times_summary(
    parent,
    info,  # noqa: WPS110
    **kwargs,
):
    """Resolve spent times summary."""
    filterset = SpentTimeFilterSet(
        data=kwargs,
        queryset=filter_allowed_for_user(
            SpentTime.objects.all(),
            info.context.user,
        ),
        request=info.context,
    )

    return spent_time_service.get_summary(filterset.qs)
