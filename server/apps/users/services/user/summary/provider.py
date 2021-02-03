from dataclasses import dataclass

import django_filters
from django.db import models

from apps.development.models import Issue, Project


@dataclass(frozen=True)
class UserIssuesSummary:
    """User issues summary."""

    assigned_count: int = 0
    created_count: int = 0
    participation_count: int = 0


class UserIssuesSummaryFilterSet(django_filters.FilterSet):
    """User issues summary filterset."""

    class Meta:
        model = Issue
        fields = "__all__"

    project = django_filters.ModelChoiceFilter(queryset=Project.objects.all())
    due_date = django_filters.DateFilter()


class UserIssuesSummaryProvider:
    """User issues summary provider."""

    filterset_class = UserIssuesSummaryFilterSet

    def __init__(self, user, **kwargs) -> None:
        """Init user issues summary provider."""
        self._user = user
        self._kwargs = kwargs

    def get_summary(self) -> UserIssuesSummary:
        """Get user issues summary."""
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.annotate(
            participation_user=self._count(participants=self._user),
        )

        return UserIssuesSummary(
            **queryset.aggregate(
                assigned_count=self._count(user=self._user),
                created_count=self._count(author=self._user),
                participation_count=models.Sum("participation_user"),
            ),
        )

    def get_queryset(self) -> models.QuerySet:
        """Get queryset."""
        return Issue.objects.all()

    def filter_queryset(self, queryset) -> models.QuerySet:
        """Filter queryset."""
        return self.filterset_class(
            data=self._kwargs,
            queryset=queryset,
        ).qs

    def _count(self, **filters) -> models.Count:
        """Count values by filters."""
        return models.Count("id", filter=models.Q(**filters))
