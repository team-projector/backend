from distutils.util import strtobool

from django.contrib.admin.filters import SimpleListFilter
from django.utils.translation import ugettext as _


class HasSalaryFilter(SimpleListFilter):
    title = 'Has Salary'
    parameter_name = 'has_salary'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes'), ),
            ('no', _('No'), ),
        )

    def queryset(self, request, queryset):
        try:
            return queryset.filter(
                salary__isnull=not strtobool(str(self.value()))
            )
        except ValueError:
            return queryset
