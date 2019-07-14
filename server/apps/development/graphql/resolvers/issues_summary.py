from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models import Issue
from apps.development.services.allowed.issues import filter_allowed_for_user
from apps.development.services.summary.issues import get_issues_summary


def resolve_issues_summary(parent, info, **kwargs):
    filterset = IssuesFilterSet(
        data=kwargs,
        queryset=filter_allowed_for_user(
            Issue.objects.all(),
            info.context.user
        ),
        request=info.context,
    )

    return get_issues_summary(
        filterset.qs,
        filterset.form.cleaned_data['due_date'],
        filterset.form.cleaned_data['user'],
        filterset.form.cleaned_data['team']
    )