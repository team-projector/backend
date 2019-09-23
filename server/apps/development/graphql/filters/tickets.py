import django_filters

from apps.development.models import Milestone, Ticket


class TicketsFilterSet(django_filters.FilterSet):
    milestone = django_filters.ModelChoiceFilter(
        queryset=Milestone.objects.all(),
    )
    order_by = django_filters.OrderingFilter(
        fields=('due_date',),
    )

    class Meta:
        model = Ticket
        fields = ('milestone',)
