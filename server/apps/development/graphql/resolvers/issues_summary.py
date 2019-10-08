# -*- coding: utf-8 -*-

from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models import Issue
from apps.development.services.summary.issues import get_issues_summary
from apps.development.services.summary.issues_project import (
    get_project_summaries,
)
from apps.development.services.summary.issues_team import get_team_summaries


def resolve_issues_summary(
    parent,
    info,
    **kwargs,
):
    """Resolve issues summary."""
    filterset = IssuesFilterSet(
        data=kwargs,
        queryset=Issue.objects.allowed_for_user(
            info.context.user,
        ),
        request=info.context,
    )

    return get_issues_summary(
        filterset.qs,
        **filterset.form.cleaned_data,
    )


def resolve_issues_project_summaries(
    parent,
    info,
    **kwargs,
):
    """Resolve issues project summaries."""
    return get_project_summaries(
        parent.queryset,
        **kwargs,
    )


def resolve_issues_team_summaries(
    parent,
    info,
    **kwargs,
):
    """Resolve issues team summaries."""
    return get_team_summaries(
        parent.queryset,
        **kwargs,
    )
