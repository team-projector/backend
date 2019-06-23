from rest_framework import filters

from apps.core.rest.filters import FilterParamUrlSerializer
from apps.core.utils.rest import parse_query_params


class IssueStatusUrlFiler(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = parse_query_params(request, FilterParamUrlSerializer)

        gl_url = params.get('url')

        if gl_url:
            queryset = queryset.filter(gl_url=gl_url)

        return queryset
