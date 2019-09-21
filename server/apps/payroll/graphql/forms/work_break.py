from django import forms
from django.contrib.auth import get_user_model

from apps.payroll.models.work_break import WORK_BREAK_REASONS

User = get_user_model()


class WorkBreakForm(forms.Form):
    id = forms.IntegerField(
        required=False,
        min_value=0
    )

    user = forms.ModelChoiceField(
        required=False,
        queryset=User.objects.all()
    )

    from_date = forms.DateTimeField(
        required=False
    )

    to_date = forms.DateTimeField(
        required=False
    )

    reason = forms.ChoiceField(
        required=False,
        choices=WORK_BREAK_REASONS
    )

    comment = forms.CharField(
        required=False,
        empty_value=None
    )