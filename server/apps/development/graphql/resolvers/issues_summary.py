from apps.core.graphql.security.authentication import auth_required
from apps.development.graphql.fields.issues import IssuesFilterSet
from apps.development.models import Issue
from apps.development.services.issue.allowed import filter_allowed_for_user
from apps.development.services.issue.summary import (
    get_issues_summary,
    get_project_summaries,
    get_team_summaries,
)


def resolve_issues_summary(
    parent,
    info,  # noqa: WPS110
    **kwargs,
):
    """Resolve issues summary."""
    auth_required(info)

    queryset = filter_allowed_for_user(Issue.objects.all(), info.context.user)
    filterset = IssuesFilterSet(
        data=kwargs,
        queryset=queryset,
        request=info.context,
    )

    return get_issues_summary(filterset.qs, **filterset.form.cleaned_data)


def resolve_issues_project_summaries(
    parent,
    info,  # noqa: WPS110
    **kwargs,
):
    """Resolve issues project summaries."""
    auth_required(info)

    return get_project_summaries(parent.queryset, **kwargs)


def resolve_issues_team_summaries(
    parent,
    info,  # noqa: WPS110
    **kwargs,
):
    """Resolve issues team summaries."""
    auth_required(info)

    return get_team_summaries(parent.queryset, **kwargs)
