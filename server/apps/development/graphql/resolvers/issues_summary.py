# -*- coding: utf-8 -*-

from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models import Issue
from apps.development.services import issue as issue_service


def resolve_issues_summary(
    parent,
    info,  # noqa WPS110
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

    return issue_service.get_issues_summary(
        filterset.qs,
        **filterset.form.cleaned_data,
    )


def resolve_issues_project_summaries(
    parent,
    info,  # noqa WPS110
    **kwargs,
):
    """Resolve issues project summaries."""
    return issue_service.get_project_summaries(
        parent.queryset,
        **kwargs,
    )


def resolve_issues_team_summaries(
    parent,
    info,  # noqa WPS110
    **kwargs,
):
    """Resolve issues team summaries."""
    return issue_service.get_team_summaries(
        parent.queryset,
        **kwargs,
    )
