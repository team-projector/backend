from rest_framework import filters
from rest_framework.compat import coreapi, coreschema


class BaseModelFilterBackend(filters.BaseFilterBackend):
    filter_title = None
    filter_description = None
    filter_param = None
    filter_lookup = None

    def __init__(self):
        super().__init__()
        if not self.filter_param:
            raise NotImplementedError('Not filled field "filter_param"')

        if not self.filter_description:
            self.filter_description = f'Filter by {self.filter_param}'

        if not self.filter_title:
            self.filter_title = self.filter_param.title()

        if not self.filter_lookup:
            self.filter_lookup = self.filter_param

    def filter_queryset(self, request, queryset, view):
        filter_value = request.GET.get(self.filter_param)
        if filter_value and filter_value.isdigit():
            query = {
                self.filter_lookup: filter_value
            }
            queryset = queryset.filter(**query)

        return queryset

    def get_schema_fields(self, view):
        super().get_schema_fields(view)

        return [
            coreapi.Field(
                name=self.filter_param,
                required=False,
                location='query',
                schema=coreschema.Integer(
                    title=self.filter_title,
                    description=self.filter_description
                )
            )
        ]
