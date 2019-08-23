from admin_tools.mixins import AdminAutocompleteFieldsMixin
from django.contrib import admin

from apps.core.admin.mixins import AdminFormFieldsOverridesMixin


class BaseModelAdmin(AdminAutocompleteFieldsMixin,
                     AdminFormFieldsOverridesMixin,
                     admin.ModelAdmin):
    list_per_page = 20

    class Media:
        pass
