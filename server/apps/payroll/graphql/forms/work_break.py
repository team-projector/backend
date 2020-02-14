# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth import get_user_model

from apps.payroll.models.work_break import WorkBreakReason

User = get_user_model()


class WorkBreakForm(forms.Form):
    """Work break form used for validation input data mutations."""

    id = forms.IntegerField(  # noqa: A003
        required=False,
        min_value=0,
    )

    user = forms.ModelChoiceField(
        required=False,
        queryset=User.objects.all(),
    )

    from_date = forms.DateTimeField(
        required=False,
    )

    to_date = forms.DateTimeField(
        required=False,
    )

    reason = forms.ChoiceField(
        required=False,
        choices=WorkBreakReason.choices,
    )

    comment = forms.CharField(
        required=False,
        empty_value=None,
    )
