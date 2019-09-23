from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models import Issue
from apps.development.services.summary.issues import get_issues_summary
from apps.development.services.summary.issues_project import (
    get_project_summaries,
)
from apps.development.services.summary.issues_team import get_team_summaries


def resolve_issues_summary(parent,
                           info,
                           **kwargs):
    filterset = IssuesFilterSet(
        data=kwargs,
        queryset=Issue.objects.allowed_for_user(
            info.context.user,
        ),
        request=info.context,
    )

    return get_issues_summary(
        filterset.qs,
        filterset.form.cleaned_data['due_date'],
        filterset.form.cleaned_data['user'],
        filterset.form.cleaned_data['team'],
        filterset.form.cleaned_data['project'],
        filterset.form.cleaned_data['state'],
        filterset.form.cleaned_data['milestone'],
    )


def resolve_issues_project_summaries(parent,
                                     info,
                                     **kwargs):
    return get_project_summaries(
        parent.queryset,
        **kwargs,
    )


def resolve_issues_team_summaries(parent,
                                  info,
                                  **kwargs):
    return get_team_summaries(
        parent.queryset,
        **kwargs,
    )
