import django_filters
from django.contrib.contenttypes.models import ContentType
from django.db.models import OuterRef, Subquery, F

from apps.core.graphql.filters import NullsAlwaysLastOrderingFilter
from apps.development.models import Project, Milestone

MILESTONE_DUE_DATE_SORT = 'milestone__dueDate'


class ProjectsFilterSet(django_filters.FilterSet):
    order_by = NullsAlwaysLastOrderingFilter(
        fields=(('due_date', MILESTONE_DUE_DATE_SORT),)
    )

    class Meta:
        model = Project
        fields = ()

    def filter_queryset(self, queryset):
        order_by = self.form.cleaned_data.get('order_by')
        if not order_by:
            return super().filter_queryset(queryset)

        if MILESTONE_DUE_DATE_SORT in order_by:
            ordering = F('due_date').asc(nulls_last=True)
        elif f'-{MILESTONE_DUE_DATE_SORT}' in order_by:
            ordering = F('due_date').desc(nulls_last=True)
        else:
            return super().filter_queryset(queryset)

        ct = ContentType.objects.get_for_model(Project)
        sub_qs = Milestone.objects. \
            filter(content_type=ct, object_id=OuterRef('pk')). \
            order_by(ordering)

        queryset = queryset.annotate(due_date=Subquery(sub_qs.values('due_date')[:1]))

        return super().filter_queryset(queryset)
