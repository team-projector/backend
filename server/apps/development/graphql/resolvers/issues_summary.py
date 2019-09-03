from django.db.models import Sum
from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models import Issue
from apps.development.services.summary.issues import (
    get_issues_summary, get_project_summaries
)
from apps.payroll.models import SpentTime


def resolve_issues_summary(parent,
                           info,
                           **kwargs):
    filterset = IssuesFilterSet(
        data=kwargs,
        queryset=Issue.objects.allowed_for_user(
            info.context.user
        ),
        request=info.context,
    )

    return get_issues_summary(
        filterset.qs,
        filterset.form.cleaned_data['due_date'],
        filterset.form.cleaned_data['user'],
        filterset.form.cleaned_data['team'],
        filterset.form.cleaned_data['project'],
        filterset.form.cleaned_data['state'],
        filterset.form.cleaned_data['milestone']
    )


def resolve_issues_project_summaries(parent,
                                     info,
                                     **kwargs):
    return get_project_summaries(
        parent.queryset,
        **kwargs
    )


def resolve_issues_summary_time_spent(parent,
                                      info,
                                      **kwargs):
    queryset = SpentTime.objects.for_issues(parent.queryset)

    return queryset.aggregate(
        total_time_spent=Sum('time_spent')
    )['total_time_spent'] or 0
