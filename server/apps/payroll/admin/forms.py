from django import forms
from django.contrib.admin import widgets


class GenerateSalariesForm(forms.Form):
    period_from = forms.DateField(widget=widgets.AdminDateWidget)
    period_to = forms.DateField(widget=widgets.AdminDateWidget)

    class Media:
        js = ('admin/js/core.js',)
