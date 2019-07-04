from rest_framework import filters, serializers

from apps.core.utils.rest import parse_query_params
from apps.development.services.problems.issues import (
    filter_issues_problems, exclude_issues_problems
)


class ParamsSerializer(serializers.Serializer):
    problems = serializers.NullBooleanField(required=False)


class IssueProblemFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = parse_query_params(request, ParamsSerializer)

        show_problem = params.get('problems')

        if show_problem is True:
            queryset = filter_issues_problems(queryset)
        elif show_problem is False:
            queryset = exclude_issues_problems(queryset)

        return queryset
