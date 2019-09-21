from django import forms

from apps.development.models import Milestone
from apps.development.models.ticket import TICKET_TYPES


class TicketForm(forms.Form):
    id = forms.IntegerField(
        required=False,
        min_value=0
    )

    type = forms.ChoiceField(
        required=False,
        choices=TICKET_TYPES
    )

    title = forms.CharField(
        required=False,
        max_length=255,
        empty_value=None
    )

    start_date = forms.DateField(
        required=False
    )

    due_date = forms.DateField(
        required=False
    )

    url = forms.URLField(
        required=False
    )

    milestone = forms.ModelChoiceField(
        required=False,
        queryset=Milestone.objects.all()
    )