from rest_framework import filters, serializers

from apps.core.utils.rest import parse_query_params


class ParamsSerializer(serializers.Serializer):
    url = serializers.URLField()


class IssueStatusUrlFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = parse_query_params(request, ParamsSerializer)

        gl_url = params.get('url')

        if gl_url:
            queryset = queryset.filter(gl_url=gl_url)

        return queryset
