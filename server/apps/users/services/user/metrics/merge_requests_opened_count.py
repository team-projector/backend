from apps.core.graphql.security.authentication import auth_required
from apps.development.models import MergeRequest
from apps.development.models.merge_request import MergeRequestState


def mr_opened_count_resolver(parent, info, **kwargs) -> int:  # noqa:WPS110
    """:returns user opened merge requests count."""
    auth_required(info)

    user = info.context.user

    if user.is_authenticated:
        return MergeRequest.objects.filter(
            user=user,
            state=MergeRequestState.OPENED,
        ).count()

    return 0
