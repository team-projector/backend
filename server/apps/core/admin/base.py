from django import forms
from django.contrib import admin


class BaseModelAdmin(admin.ModelAdmin):
    list_per_page = 20


class BaseStackedInline(admin.StackedInline):
    extra = 0
    show_change_link = True


class BaseTabularInline(admin.TabularInline):
    extra = 0
    show_change_link = True


class BaseModelForm(forms.ModelForm):
    pass
