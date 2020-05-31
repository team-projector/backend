# -*- coding: utf-8 -*-

from django import forms
from django.contrib.admin import widgets


class GenerateSalaryForm(forms.Form):
    """Generate salaries form."""

    class Media:
        js = ("admin/js/core.js",)

    period_from = forms.DateField(widget=widgets.AdminDateWidget)
    period_to = forms.DateField(widget=widgets.AdminDateWidget)
