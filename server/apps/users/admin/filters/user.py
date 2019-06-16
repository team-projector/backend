from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from admin_auto_filters.filters import AutocompleteFilter


class UserFilter(AutocompleteFilter):
    title = 'User'
    field_name = 'user'


class UserActiveFilter(SimpleListFilter):
    title = _('Is Active')

    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
            ('all', _('All')),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(is_active=True)
        elif self.value() == 'no':
            return queryset.filter(is_active=False)

        return queryset
