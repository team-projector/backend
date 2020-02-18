# -*- coding: utf-8 -*-

from django.db import models

from apps.development.models.milestone import MilestoneState


class MilestonesSummaryProvider:
    """Provides summary of milestones."""

    def __init__(self, queryset, fields=()):
        """
        Initialise a provider with queryset and optional fields.

        :param queryset: Milestones queryset
        :param fields: MilestonesSummaryType.fields required for aggregation.
        """
        self._fields = fields
        self._queryset = queryset

    def get_data(self):
        """Returns aggregation on only selected fields."""
        aggregations = {
            "count": models.Count("*"),
            "active_count": models.Count(
                "id", filter=models.Q(state=MilestoneState.ACTIVE),
            ),
            "closed_count": models.Count(
                "id", filter=models.Q(state=MilestoneState.CLOSED),
            ),
        }

        if self._fields:
            fields_set = set(self._fields)
            aggregations = {
                name: aggr
                for name, aggr
                in aggregations.items() if name in fields_set
            }

        return self._queryset.aggregate(**aggregations)
