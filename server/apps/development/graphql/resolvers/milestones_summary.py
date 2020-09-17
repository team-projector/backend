# -*- coding: utf-8 -*-

from apps.core.graphql import get_fields_from_info
from apps.development.graphql.filters import MilestonesFilterSet
from apps.development.models import Milestone
from apps.development.services.milestone.allowed import filter_allowed_for_user
from apps.development.services.milestone.summary import (
    MilestonesSummaryProvider,
)


def resolve_milestones_summary(
    parent,
    info,  # noqa: WPS110
    **kwargs,
):
    """Resolve issues summary."""
    filterset = MilestonesFilterSet(
        data=kwargs,
        queryset=filter_allowed_for_user(
            Milestone.objects.all(),
            info.context.user,
        ),
        request=info.context,
    )

    return MilestonesSummaryProvider(
        filterset.qs,
        fields=get_fields_from_info(info),
    ).get_data()
