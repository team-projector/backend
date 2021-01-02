from apps.development.graphql.fields.merge_requests import (
    MergeRequestFilterSet,
)
from apps.development.models import MergeRequest
from apps.development.services.merge_request.allowed import (
    filter_allowed_for_user,
)
from apps.development.services.merge_request.summary import (
    get_merge_requests_summary,
)


def resolve_merge_requests_summary(parent, info, **kwargs):  # noqa: WPS110
    """Resolve merge requests summary."""
    queryset = filter_allowed_for_user(
        MergeRequest.objects.all(),
        info.context.user,
    )

    filterset = MergeRequestFilterSet(
        data=kwargs,
        queryset=queryset,
        request=info.context,
    )

    return get_merge_requests_summary(filterset.qs)
