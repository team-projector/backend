from apps.development.graphql.filters import MergeRequestFilterSet
from apps.development.models import MergeRequest
from apps.development.services.summary.merge_requests import \
    get_merge_requests_summary


def resolve_merge_requests_summary(parent, info, **kwargs):
    filterset = MergeRequestFilterSet(
        data=kwargs,
        queryset=MergeRequest.objects.allowed_for_user(info.context.user),
        request=info.context,
    )

    return get_merge_requests_summary(
        filterset.qs,
        filterset.form.cleaned_data['project'],
        filterset.form.cleaned_data['team'],
        filterset.form.cleaned_data['user']
    )
