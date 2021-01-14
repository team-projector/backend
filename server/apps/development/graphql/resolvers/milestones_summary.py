from jnt_django_graphene_toolbox.helpers.selected_fields import (
    get_fields_from_info,
)

from apps.core.graphql.security.authentication import auth_required
from apps.development.graphql.fields import MilestonesFilterSet
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
    auth_required(info)

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
