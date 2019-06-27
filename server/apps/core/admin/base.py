from admin_tools.mixins import AdminAutocompleteFieldsMixin
from django import forms
from django.contrib import admin
from django.contrib.contenttypes.admin import (
    GenericStackedInline, GenericTabularInline
)

from apps.core.admin.mixins import AdminFormFieldsOverridesMixin


class BaseModelAdmin(AdminAutocompleteFieldsMixin,
                     AdminFormFieldsOverridesMixin,
                     admin.ModelAdmin):
    list_per_page = 20

    class Media:
        pass


class BaseStackedInline(AdminAutocompleteFieldsMixin,
                        AdminFormFieldsOverridesMixin,
                        admin.StackedInline):
    extra = 0
    show_change_link = True


class BaseTabularInline(AdminAutocompleteFieldsMixin,
                        AdminFormFieldsOverridesMixin,
                        admin.TabularInline):
    extra = 0
    show_change_link = True


class BaseGenericStackedInline(AdminAutocompleteFieldsMixin,
                               AdminFormFieldsOverridesMixin,
                               GenericStackedInline):
    extra = 0
    show_change_link = True


class BaseGenericTabularInline(AdminAutocompleteFieldsMixin,
                               AdminFormFieldsOverridesMixin,
                               GenericTabularInline):
    extra = 0
    show_change_link = True


class BaseModelForm(forms.ModelForm):
    pass
