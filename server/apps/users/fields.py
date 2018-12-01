from django import forms
from django.contrib.auth.models import Permission

from .widgets import PermissionSelectMultipleWidget


class PermissionSelectMultipleField(forms.ModelMultipleChoiceField):
    widget = PermissionSelectMultipleWidget

    def __init__(self, queryset=None, *args, **kwargs):
        if queryset is None:
            queryset = Permission.objects.all()
        super().__init__(queryset, *args, **kwargs)
