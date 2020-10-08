from distutils.util import strtobool

from django.contrib.admin.filters import SimpleListFilter
from django.utils.translation import gettext as _


class HasSalaryFilter(SimpleListFilter):
    """Has salary filter."""

    title = "Has Salary"
    parameter_name = "has_salary"

    def lookups(self, request, model_admin):
        """Get lookups."""
        return (
            ("yes", _("Yes")),
            ("no", _("No")),
        )

    def queryset(self, request, queryset):
        """Get queryset."""
        try:
            return queryset.filter(
                salary__isnull=not strtobool(str(self.value())),
            )
        except ValueError:
            return queryset
