from typing import Dict

import django_filters
from django.db import models
from graphql import ResolveInfo

from apps.core.graphql.security.authentication import auth_required
from apps.development.models import Issue, Project
from apps.users.models import User


class UserIssuesSummaryFilterSet(django_filters.FilterSet):
    """User issues summary filterset."""

    class Meta:
        model = Issue
        fields = "__all__"

    project = django_filters.ModelChoiceFilter(queryset=Project.objects.all())
    due_date = django_filters.DateFilter()


def resolve_user_issues_summary(
    parent: User,
    info: ResolveInfo,  # noqa: WPS110
    **kwargs,
) -> Dict[str, int]:
    """Get issue summary for user."""
    auth_required(info)

    queryset = UserIssuesSummaryFilterSet(
        data=kwargs,
        queryset=Issue.objects.all(),
    ).qs

    aggregations = {
        "assigned_count": models.Count("id", filter=models.Q(user=parent)),
        "created_count": models.Count("id", filter=models.Q(author=parent)),
        "participation_count": models.Count(
            "id",
            filter=models.Q(participants=parent),
        ),
    }

    return queryset.aggregate(**aggregations)
