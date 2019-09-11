from apps.development.graphql.filters import MergeRequestFilterSet
from apps.development.models import MergeRequest
from ...services.summary.merge_requests import get_merge_requests_summary


def resolve_merge_requests_summary(parent, info, **kwargs):
    filterset = MergeRequestFilterSet(
        data=kwargs,
        queryset=MergeRequest.objects.allowed_for_user(info.context.user),
        request=info.context,
    )

    return get_merge_requests_summary(
        filterset.qs
    )
