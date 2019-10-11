# -*- coding: utf-8 -*-

from apps.development.graphql.filters import MergeRequestFilterSet
from apps.development.models import MergeRequest

from ...services.merge_request.summary import get_merge_requests_summary


def resolve_merge_requests_summary(parent, info, **kwargs):  # noqa WPS110
    """Resolve merge requests summary."""
    filterset = MergeRequestFilterSet(
        data=kwargs,
        queryset=MergeRequest.objects.allowed_for_user(info.context.user),
        request=info.context,
    )

    return get_merge_requests_summary(
        filterset.qs,
    )
