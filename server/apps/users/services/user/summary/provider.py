from dataclasses import dataclass

import django_filters
from django.db import models

from apps.development.models import Issue, Project
from apps.development.models.issue import IssueState


@dataclass(frozen=True)
class UserIssuesSummary:
    """User issues summary."""

    assigned_count: int = 0
    assigned_opened_count: int = 0
    created_count: int = 0
    created_opened_count: int = 0
    participation_count: int = 0
    participation_opened_count: int = 0


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
        pk_field = "pk"
        queryset = self.filter_queryset(self.get_queryset())

        participants = Issue.participants.through.objects.filter(
            user=self._user,
            issue_id=models.OuterRef(pk_field),
        ).values(pk_field)

        participants_opened = Issue.participants.through.objects.filter(
            user=self._user,
            issue__state=IssueState.OPENED,
            issue_id=models.OuterRef(pk_field),
        ).values(pk_field)

        queryset = queryset.annotate(
            has_participant=models.Case(
                models.When(models.Exists(participants), then=1),
                default=0,
                output_field=models.IntegerField(),
            ),
            has_participant_opened=models.Case(
                models.When(models.Exists(participants_opened), then=1),
                default=0,
                output_field=models.IntegerField(),
            ),
        )

        return UserIssuesSummary(
            **queryset.aggregate(
                assigned_count=self._count(user=self._user),
                assigned_opened_count=self._count(
                    user=self._user,
                    state=IssueState.OPENED,
                ),
                created_count=self._count(author=self._user),
                created_opened_count=self._count(
                    author=self._user,
                    state=IssueState.OPENED,
                ),
                participation_count=models.Sum("has_participant"),
                participation_opened_count=models.Sum(
                    "has_participant_opened",
                ),
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
