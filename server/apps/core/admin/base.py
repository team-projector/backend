from django import forms
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline, GenericTabularInline


class BaseModelAdmin(admin.ModelAdmin):
    list_per_page = 20


class BaseStackedInline(admin.StackedInline):
    extra = 0
    show_change_link = True


class BaseTabularInline(admin.TabularInline):
    extra = 0
    show_change_link = True


class BaseGenericStackedInline(GenericStackedInline):
    extra = 0
    show_change_link = True


class BaseGenericTabularInline(GenericTabularInline):
    extra = 0
    show_change_link = True


class BaseModelForm(forms.ModelForm):
    pass
