from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

YES_VALUE = "yes"
NO_VALUE = "no"


class ProblemsFilter(admin.SimpleListFilter):
    """List filter by has problem."""

    title = _("VN__HAS_PROBLEMS")
    parameter_name = "has_problem"

    def lookups(self, request, model_admin):
        """Returns a list of tuples available filter values."""
        return (
            (YES_VALUE, _("Yes")),
            (NO_VALUE, _("No")),
        )

    def queryset(self, request, queryset) -> models.QuerySet:
        """Filtering queryset by value."""
        from apps.development.graphql.fields import (  # noqa: WPS433
            issues_filters,
        )

        problem_filter = issues_filters.ProblemsFilter()

        return problem_filter.filter(queryset, self._get_current_value())

    def _get_current_value(self):
        current_value = self.value()
        values_map = {
            YES_VALUE: True,
            NO_VALUE: False,
        }

        return values_map.get(current_value)
