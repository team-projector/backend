# -*- coding: utf-8 -*-

from admin_tools.mixins import AdminAutocompleteFieldsMixin
from django.contrib.contenttypes.admin import GenericTabularInline

from apps.core.admin.mixins import AdminFormFieldsOverridesMixin


class BaseGenericTabularInline(AdminAutocompleteFieldsMixin,
                               AdminFormFieldsOverridesMixin,
                               GenericTabularInline):
    extra = 0
    show_change_link = True
