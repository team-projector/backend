# -*- coding: utf-8 -*-

import django_filters
from django.db.models import QuerySet

from apps.core.graphql.filters.ordering import OrderingFilter
from apps.development.models import MergeRequest, Project, Team, TeamMember
from apps.users.models import User


class TeamFilter(django_filters.ModelChoiceFilter):
    """Filter issues by team."""

    def __init__(self) -> None:
        super().__init__(queryset=Team.objects.all())

    def filter(self, queryset, value) -> QuerySet:
        """Do filtering."""
        if not value:
            return queryset

        users = TeamMember.objects.get_no_watchers(value)
        return queryset.filter(user__in=users)


class MergeRequestFilterSet(django_filters.FilterSet):
    """Set of filters for Merge Request."""

    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    project = django_filters.ModelChoiceFilter(queryset=Project.objects.all())
    team = TeamFilter()

    order_by = OrderingFilter(
        fields=('title', 'created_at', 'closed_at'),
    )

    class Meta:
        model = MergeRequest
        fields = ('state', 'user', 'team', 'project')
