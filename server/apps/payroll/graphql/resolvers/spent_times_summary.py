from apps.payroll.graphql.filters import SpentTimeFilterSet
from apps.payroll.models import SpentTime
from apps.payroll.services.summary.spent_times import \
    get_spent_times_summary


def resolve_spent_times_summary(parent,
                                info,
                                **kwargs):
    filterset = SpentTimeFilterSet(
        data=kwargs,
        queryset=SpentTime.objects.allowed_for_user(
            info.context.user
        ),
        request=info.context,
    )

    return get_spent_times_summary(
        filterset.qs
    )
