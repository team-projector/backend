from django import forms

from apps.development.models import Milestone, Ticket


class TicketForm(forms.Form):
    id = forms.IntegerField(
        required=False,
        min_value=0,
    )
    type = forms.ChoiceField(
        required=False,
        choices=Ticket.TYPE,
    )
    title = forms.CharField(
        required=False,
        max_length=255,
        empty_value=None,
    )
    start_date = forms.DateField(
        required=False,
    )
    due_date = forms.DateField(
        required=False,
    )
    url = forms.URLField(
        required=False,
    )
    milestone = forms.ModelChoiceField(
        required=False,
        queryset=Milestone.objects.all(),
    )
