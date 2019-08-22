import django_filters

from apps.development.models import Feature, Milestone


class FeaturesFilterSet(django_filters.FilterSet):
    milestone = django_filters.ModelChoiceFilter(
        queryset=Milestone.objects.all()
    )

    class Meta:
        model = Feature
        fields = ('milestone',)
