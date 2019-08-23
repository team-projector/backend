from admin_tools.mixins import AdminAutocompleteFieldsMixin
from django.contrib.contenttypes.admin import GenericStackedInline

from apps.core.admin.mixins import AdminFormFieldsOverridesMixin


class BaseGenericStackedInline(AdminAutocompleteFieldsMixin,
                               AdminFormFieldsOverridesMixin,
                               GenericStackedInline):
    extra = 0
    show_change_link = True
