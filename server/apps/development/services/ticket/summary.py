from typing import Dict

from django.db import models

from apps.development.models.ticket import TicketState


class TicketsSummaryProvider:
    """Provides summary of tickets."""

    def __init__(self, queryset, fields=()):
        """
        Initialise a provider with queryset and optional fields.

        :param queryset: Tickets queryset
        :param fields: TicketsSummaryType fields required to be in aggregation.
        """
        self._fields = fields
        self._queryset = queryset

    def get_data(self):
        """Returns aggregation on only selected fields."""
        aggregations = self._get_fields_expressions()

        if self._fields:
            fields_set = set(self._fields)
            aggregations = {
                name: aggr
                for name, aggr in aggregations.items()
                if name in fields_set
            }

        return self._queryset.aggregate(**aggregations)

    def _get_fields_expressions(self) -> Dict[str, models.Aggregate]:
        """
        Get fields expressions.

        :rtype: Dict[str, Aggregate]
        """
        state_fields = {
            "{0}_count".format(state.lower()): state
            for state in TicketState.values
        }

        state_expressions = {
            field: models.Count("id", filter=models.Q(state=state))
            for field, state in state_fields.items()
        }

        return {"count": models.Count("*"), **state_expressions}
